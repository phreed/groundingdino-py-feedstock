"""Strip an installed groundingdino down to its compiled extension.

The cuda output builds the whole wheel because that is the only way setup.py
will compile ``groundingdino._C``, but it must ship *only* the extension:
every ``.py`` in the tree is already owned by groundingdino-py-base, and two
conda packages claiming the same file is an error at install time.

Usage: python prune_to_extension.py <site-packages>/groundingdino
"""

import sys
from pathlib import Path


def prune(pkg_dir: Path) -> None:
    if not pkg_dir.is_dir():
        raise SystemExit(f"not a directory: {pkg_dir}")

    kept = sorted(pkg_dir.glob("_C*.so"))
    if not kept:
        # Failing loudly matters here.  A silent miss would publish an empty
        # cuda package that installs cleanly and then falls back to the slow
        # path at run time, which is very hard to notice.
        raise SystemExit(f"no compiled extension found in {pkg_dir}")

    keep = {p.resolve() for p in kept}
    removed = 0
    for path in sorted(pkg_dir.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path.is_dir():
            # rmdir only succeeds once the directory is empty, which is exactly
            # the condition for removing it.
            try:
                path.rmdir()
            except OSError:
                pass
        elif path.resolve() not in keep:
            path.unlink()
            removed += 1

    print(f"kept {[p.name for p in kept]}, removed {removed} file(s)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    prune(Path(sys.argv[1]))
