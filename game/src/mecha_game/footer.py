"""Readable casing text; pygame-independent layout, no engine calculations."""
from dataclasses import dataclass
from collections.abc import Callable

HELP_LINES = (
    'HELP — companion time is paused',
    'F feed   P play   S sleep   G clean when enabled',
    'Ctrl+S save now; after a save failure, retry the save',
    'Save failure pauses care; Ctrl+Q quits without saving',
    'Enter adopt successor after death',
    'T era reports (care paused): [ ] era, PgUp/PgDn pages',
    'In reports: B archive, E next era, C covenant, T/Escape close',
    'E run an era   C covenant budget   H hatch founder',
    '1–5 weather: calm / stable soup / storm / real / callback',
    'A adopt selected elite, or the latest era’s best',
    'R stage current pet genome; your companion stays with you',
    'W gather workshop creatures; exact repeats stage only once',
    'Backspace unstages contributions; source creatures stay intact',
    'Weather, staged creatures and covenant changes save immediately',
    'E runs the prepared era, or finishes saving its completed result',
    'During eras: care pauses; Escape cancels before saving; F1 help',
    'Era counts are real completed work; close waits for safe shutdown',
    'V saved replay (care paused): Space play/pause, . step, , back',
    'Replay: V/Escape back, T selected report; F1 pauses playback',
    'B saved archive (care paused): . next, , previous, [ / ] era',
    'In archives: N exact saved niche history; N/B/Escape returns',
    'History: , . occurrences; T selected report, V saved recording, A adopt',
    'In archives: A adopt, T selected report, B/Escape back',
    'T campaign story: Ctrl+[ / Ctrl+] recorded predecessor campaigns',
    'Campaign links and matching niche labels do not infer ancestry',
    'L lineage: . next life, , previous life',
    'X export covenant   I covenant inbox   K pack inbox',
    'In inboxes: care pauses; , . or arrows select; Enter imports',
    'I/K or Escape back; F5 refresh; Home/End first/last file',
    'Packs stage files; I chooses a covenant; W gathers creatures after closing',
    'F1 or Escape close help   Escape in play quits',
    'PgUp / PgDn or mouse wheel browse long casing text',
)

def wrap_lines(lines, measure: Callable[[str], int], width: int) -> list[str]:
    """Wrap measured words, splitting long identifiers without truncation."""
    if width <= 0:
        raise ValueError('Text width must be positive.')
    result=[]
    for source in lines:
        for paragraph in source.splitlines() or ['']:
            line=''
            for word in paragraph.split():
                candidate=f'{line} {word}' if line else word
                if measure(candidate) <= width:
                    line=candidate
                    continue
                if line:
                    result.append(line)
                    line=''
                while measure(word) > width:
                    low,high=1,len(word)
                    if measure(word[:1]) > width:
                        raise ValueError('Text width cannot fit one glyph.')
                    while low < high:
                        middle=(low+high+1)//2
                        if measure(word[:middle]) <= width: low=middle
                        else: high=middle-1
                    result.append(word[:low])
                    word=word[low:]
                line=word
            if line:
                result.append(line)
    return result

@dataclass(frozen=True)
class FooterPage:
    lines: tuple[str,...]
    page: int
    page_count: int

@dataclass
class FooterPager:
    page: int = 0
    _page_count: int = 1

    def reset(self) -> None:
        self.page=0

    def move(self, delta: int) -> None:
        self.page=max(0,min(self._page_count-1,self.page+delta))

    def layout(self, lines, measure, width: int, rows: int) -> FooterPage:
        if rows < 2:
            raise ValueError('The casing needs room for text and paging.')
        wrapped=wrap_lines(lines,measure,width)
        if len(wrapped) <= rows:
            self._page_count=1
            self.page=0
            return FooterPage(tuple(wrapped),0,1)
        capacity=rows-1
        self._page_count=(len(wrapped)+capacity-1)//capacity
        self.page=max(0,min(self._page_count-1,self.page))
        start=self.page*capacity
        visible=wrapped[start:start+capacity]
        navigation=f'PgUp/PgDn · wheel   {self.page+1}/{self._page_count}'
        if measure(navigation)>width:
            navigation=f'PgUp/PgDn {self.page+1}/{self._page_count}'
        if measure(navigation)>width:
            raise ValueError('Casing is too narrow for paging controls.')
        return FooterPage(tuple([*visible,navigation]),self.page,self._page_count)
