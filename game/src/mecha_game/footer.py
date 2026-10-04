"""Readable casing text; pygame-independent layout, no engine calculations."""
from dataclasses import dataclass
from collections.abc import Callable

HELP_LINES = (
    'HELP — companion time is paused',
    'F feed   P play   S sleep   G clean when enabled',
    'Enter adopt successor after death',
    'E run an era   C covenant budget   H hatch founder',
    '1–5 weather: calm / stable soup / storm / real / callback',
    'A adopt selected elite, or the latest era’s best',
    'R release companion   W gather workshop creatures',
    'V review replay: Space play/pause, . step, , back',
    'B repertoire: . next, , previous, [ / ] era',
    'L lineage: . next life, , previous life',
    'X export covenant   I import covenant   K import pack',
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
