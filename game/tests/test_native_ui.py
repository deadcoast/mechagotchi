"""Native UI source-event checks; these do not claim OS keyboard automation."""
import os
import sys
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "game/src"))
import pygame
from mecha_game.native_ui import ActionStrip, StartupView, UiAction, fit_native_layout


def inspection(primary="invalid", backup="valid", actions=None):
    def save(status):
        return SimpleNamespace(status=status, reason="Invalid JSON" if status == "invalid" else None,
            name="Moss", keeper_id="keeper-original", life_id="life-2", learning_policy="qtable",
            alive=True, session_tick=123, life_count=2, digest="opaque-file")
    return SimpleNamespace(home=Path("C:/saved homes/Moss"), revision="opaque-inspected-revision",
        home_status="directory", reason=None, primary=save(primary), backup=save(backup),
        can_restore=backup == "valid" and primary in ("missing", "valid", "invalid"),
        actions=actions or ("inspect_backup", "new", "choose_directory", "retry", "quit"), notices=())


def key(code, mod=0, up=False, repeat=False):
    return pygame.event.Event(pygame.KEYUP if up else pygame.KEYDOWN, key=code, mod=mod, repeat=repeat)


class NativeUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env=patch.dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy")
        cls.env.start()
        pygame.init()
        cls.font=pygame.font.Font(None, 22)

    @classmethod
    def tearDownClass(cls):
        pygame.quit()
        cls.env.stop()

    def setUp(self):
        self.surface=pygame.Surface((640, 620))

    def click(self, widget, action):
        pos=widget.button_rects[action].center
        widget.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos))
        return widget.handle(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1, pos=pos))

    def test_startup_needs_no_session_or_filesystem_and_shows_independent_states(self):
        state=inspection()
        with patch.object(Path, "mkdir", side_effect=AssertionError("UI must not write")), \
                patch.object(Path, "read_bytes", side_effect=AssertionError("UI must not read")):
            view=StartupView(state)
            view.draw(self.surface,self.font)
            text=" ".join(view.lines)
            self.assertIn("Primary: invalid",text)
            self.assertIn("Backup: valid",text)
            self.assertIn("qtable",text)
            self.assertNotIn("resume",view.button_rects)
            self.assertEqual("opaque-inspected-revision",view.inspection.revision)

    def test_restore_requires_draw_later_input_and_defaults_to_cancel(self):
        view=StartupView(inspection())
        view.draw(self.surface,self.font)
        view.strip.focus("inspect_backup")
        self.assertIsNone(view.handle(key(pygame.K_RETURN)).action)
        self.assertEqual("backup",view.mode)
        self.assertEqual("cancel",view.focused_id)
        view.strip.focus("confirm_restore")
        self.assertIsNone(view.handle(key(pygame.K_RETURN)).action)
        view.draw(self.surface,self.font)
        self.assertIsNone(view.handle(key(pygame.K_RETURN,repeat=True)).action)
        view.handle(key(pygame.K_RETURN,up=True))
        result=view.handle(key(pygame.K_RETURN))
        self.assertEqual("confirm_restore",result.action)
        self.assertEqual(view.inspection.revision,result.inspection_revision)
        self.assertIsNone(view.handle(key(pygame.K_RETURN)).action)

    def test_new_confirmation_cancel_is_read_only(self):
        state=inspection(primary="valid")
        view=StartupView(state)
        view.draw(self.surface,self.font)
        self.click(view,"new")
        self.assertEqual("new",view.mode)
        self.assertEqual("cancel",view.focused_id)
        view.draw(self.surface,self.font)
        result=self.click(view,"cancel")
        self.assertIsNone(result.action)
        self.assertEqual("home",view.mode)
        self.assertIs(state,view.inspection)

    def test_mouse_clickthrough_and_dragging_out_cannot_confirm(self):
        view=StartupView(inspection())
        view.draw(self.surface,self.font)
        self.click(view,"inspect_backup")
        self.assertEqual("backup",view.mode)
        self.assertIsNone(view.handle(pygame.event.Event(pygame.MOUSEBUTTONUP,button=1,pos=(300,550))).action)
        view.draw(self.surface,self.font)
        pos=view.button_rects["confirm_restore"].center
        view.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=pos))
        result=view.handle(pygame.event.Event(pygame.MOUSEBUTTONUP,button=1,pos=(0,0)))
        self.assertIsNone(result.action)
        view.draw(self.surface,self.font)
        self.assertEqual("confirm_restore",self.click(view,"confirm_restore").action)

    def test_directory_unicode_edit_apply_and_cancel_keep_authority_separate(self):
        view=StartupView(inspection())
        view.draw(self.surface,self.font)
        self.click(view,"choose_directory")
        view.draw(self.surface,self.font)
        view.handle(key(pygame.K_a,pygame.KMOD_CTRL))
        value="C:/Keeper homes/森/"+"long/"*30
        view.handle(pygame.event.Event(pygame.TEXTINPUT,text=value))
        self.assertEqual(value,view.directory_text)
        view.handle(key(pygame.K_END))
        view.handle(key(pygame.K_BACKSPACE))
        view.handle(pygame.event.Event(pygame.TEXTINPUT,text="Z"))
        view.draw(self.surface,self.font)
        result=self.click(view,"apply_directory")
        self.assertEqual("choose_directory",result.action)
        self.assertEqual(value[:-1]+"Z",result.directory)
        self.assertEqual(Path("C:/saved homes/Moss"),view.inspection.home)
        view.handle(key(pygame.K_ESCAPE))
        self.assertEqual("home",view.mode)
        self.assertEqual(Path("C:/saved homes/Moss"),view.inspection.home)

    def test_directory_keyboard_can_return_to_path_after_visiting_buttons(self):
        view=StartupView(inspection())
        view.draw(self.surface,self.font)
        self.click(view,"choose_directory")
        view.draw(self.surface,self.font)
        view.handle(key(pygame.K_TAB))
        self.assertEqual("cancel",view.focused_id)
        view.handle(key(pygame.K_TAB))
        self.assertEqual("apply_directory",view.focused_id)
        view.handle(key(pygame.K_TAB))
        view.handle(key(pygame.K_a,pygame.KMOD_CTRL))
        view.handle(pygame.event.Event(pygame.TEXTINPUT,text="C:/revised"))
        self.assertEqual("C:/revised",view.directory_text)
        view.handle(key(pygame.K_TAB,pygame.KMOD_SHIFT))
        self.assertEqual("apply_directory",view.focused_id)

    def test_unseen_keyboard_page_cannot_activate_until_drawn(self):
        strip=ActionStrip([UiAction(str(i),f"Action number {i}") for i in range(18)])
        rect=pygame.Rect(8,430,368,160)
        strip.draw(self.surface,self.font,rect)
        strip.focus("17")
        self.assertIsNone(strip.handle(key(pygame.K_RETURN)).action)
        strip.handle(key(pygame.K_RETURN,up=True))
        strip.draw(self.surface,self.font,rect)
        self.assertEqual("17",strip.handle(key(pygame.K_RETURN)).action)

    def test_valid_backup_with_unreadable_primary_cannot_restore(self):
        view=StartupView(inspection(primary="unreadable"))
        view.draw(self.surface,self.font)
        self.click(view,"inspect_backup")
        view.draw(self.surface,self.font)
        self.assertIn("Restore unavailable"," ".join(view.lines))
        self.assertIsNone(self.click(view,"confirm_restore").action)

    def test_path_paste_is_explicit_and_retains_unicode(self):
        view=StartupView(inspection())
        view.draw(self.surface,self.font)
        self.click(view,"choose_directory")
        view.draw(self.surface,self.font)
        view.handle(key(pygame.K_a,pygame.KMOD_CTRL))
        with patch('pygame.scrap.get_text',return_value="C:/saved homes/森") as clipboard:
            view.handle(key(pygame.K_v,pygame.KMOD_CTRL))
            clipboard.assert_called_once()
        self.assertEqual("C:/saved homes/森",view.directory_text)

    def test_error_returns_to_actionable_home_without_inventing_state(self):
        view=StartupView(inspection())
        view.show_error("Cannot write selected home: permission denied")
        view.draw(self.surface,self.font)
        self.assertIn("permission denied"," ".join(view.lines))
        self.assertIn("choose_directory",view.button_rects)
        self.assertIn("retry",view.button_rects)
        self.assertEqual("retry",self.click(view,"retry").action)

    def test_strip_keyboard_skips_disabled_preserves_mode_tab_and_reports_pause(self):
        strip=ActionStrip([UiAction("feed","Feed"),UiAction("clean","Clean",enabled=False),UiAction("era","Run era")],allow_tab=False)
        strip.draw(self.surface,self.font,pygame.Rect(8,430,624,180))
        self.assertFalse(strip.handle(key(pygame.K_TAB)).consumed)
        self.assertTrue(strip.handle(key(pygame.K_F6)).focus_active)
        self.assertEqual("feed",strip.focused_id)
        strip.handle(key(pygame.K_RIGHT))
        self.assertEqual("era",strip.focused_id)
        self.assertEqual("era",strip.handle(key(pygame.K_SPACE)).action)
        self.assertTrue(strip.handle(key(pygame.K_ESCAPE)).consumed)
        self.assertFalse(strip.focus_active)

    def test_strip_mouse_does_not_pause_or_activate_disabled(self):
        strip=ActionStrip([UiAction("feed","Feed"),UiAction("clean","Clean",enabled=False)])
        strip.draw(self.surface,self.font,pygame.Rect(8,430,624,180))
        self.assertIsNone(self.click(strip,"clean").action)
        self.assertEqual("feed",self.click(strip,"feed").action)
        self.assertFalse(strip.focus_active)

    def test_every_action_keyboard_and_mouse_reachable_across_widths(self):
        actions=[UiAction(str(i),f"Action number {i}") for i in range(18)]
        for width in (384,640,1024):
            with self.subTest(width=width):
                surface=pygame.Surface((width,520))
                strip=ActionStrip(actions)
                rect=pygame.Rect(8,350,width-16,160)
                strip.draw(surface,self.font,rect)
                strip.focus("0")
                reached=[]
                for _ in actions:
                    strip.draw(surface,self.font,rect)
                    reached.append(strip.focused_id)
                    self.assertIn(strip.focused_id,strip.button_rects)
                    strip.handle(key(pygame.K_RIGHT))
                self.assertEqual([a.id for a in actions],reached)
                strip.blur()
                strip.page=0
                clicked=[]
                for _ in range(strip.page_count):
                    strip.draw(surface,self.font,rect)
                    ids=list(strip.button_rects)
                    for action_id in ids:
                        self.assertEqual(action_id,self.click(strip,action_id).action)
                        clicked.append(action_id)
                        strip.draw(surface,self.font,rect)
                    if "next" in strip.navigation_rects:
                        pos=strip.navigation_rects["next"].center
                        strip.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=pos))
                        strip.handle(pygame.event.Event(pygame.MOUSEBUTTONUP,button=1,pos=pos))
                self.assertEqual([a.id for a in actions],clicked)

    def test_layout_contains_separate_regions_and_integer_pixels(self):
        for size in ((384,480),(640,620),(1024,768)):
            layout=fit_native_layout(size,(16,22),self.font.get_height())
            bounds=pygame.Rect((0,0),size)
            for rect in (layout.lcd_rect,layout.footer_rect,layout.actions_rect):
                self.assertTrue(bounds.contains(rect))
            self.assertFalse(layout.lcd_rect.colliderect(layout.footer_rect))
            self.assertFalse(layout.footer_rect.colliderect(layout.actions_rect))
            self.assertEqual((16*layout.scale,22*layout.scale),layout.lcd_rect.size)
            self.assertGreaterEqual(layout.footer_rows,2)
            source=pygame.Surface((16,22));source.fill((64,100,44));source.set_at((3,2),(18,23,16))
            grown=pygame.transform.scale(source,layout.lcd_rect.size)
            self.assertEqual(source.get_at((3,2)),grown.get_at((3*layout.scale,2*layout.scale)))

    def test_resize_keeps_focus_and_drawing_does_not_touch_creature(self):
        strip=ActionStrip([UiAction(str(i),f"Action {i}") for i in range(10)])
        strip.focus("7")
        for size in ((640,620),(384,480)):
            layout=fit_native_layout(size,(16,22),self.font.get_height())
            surface=pygame.Surface(size);surface.fill((44,67,22))
            before=pygame.image.tobytes(surface.subsurface(layout.lcd_rect),"RGB")
            strip.draw(surface,self.font,layout.actions_rect)
            self.assertEqual("7",strip.focused_id)
            self.assertIn("7",strip.button_rects)
            self.assertEqual(before,pygame.image.tobytes(surface.subsurface(layout.lcd_rect),"RGB"))


if __name__ == "__main__":
    unittest.main()
