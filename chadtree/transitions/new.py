from os.path import dirname, exists, join
from typing import Optional

from pynvim import Nvim
from pynvim_pp.lib import s_write

from ..fs.cartographer import is_dir
from ..fs.ops import ancestors, new
from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from .shared.index import indices
from .shared.open_file import open_file
from .shared.refresh import refresh
from .types import ClickType, Stage


@rpc(blocking=False)
def _new(
    nvim: Nvim, state: State, settings: Settings, is_visual: bool
) -> Optional[Stage]:
    """
    new file / folder
    """

    node = next(indices(nvim, state=state, is_visual=is_visual), None) or state.root
    parent = node.path if is_dir(node) else dirname(node.path)

    child: Optional[str] = nvim.funcs.input(LANG("pencil"))

    if child:
        path = join(parent, child)
        if exists(path):
            s_write(nvim, LANG("already_exists", name=path), error=True)
            return Stage(state)
        else:
            try:
                new(path)
            except Exception as e:
                s_write(nvim, e, error=True)
                return refresh(nvim, state=state, settings=settings)
            else:
                paths = ancestors(path)
                _index = state.index | paths
                new_state = forward(state, settings=settings, index=_index, paths=paths)
                nxt = open_file(
                    nvim,
                    state=new_state,
                    settings=settings,
                    path=path,
                    click_type=ClickType.secondary,
                )
                return nxt
    else:
        return None
