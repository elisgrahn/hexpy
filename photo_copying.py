import argparse
import os
import os.path as osp
import shutil
from pathlib import Path

from tqdm import tqdm


def parse_args() -> argparse.Namespace:
    """Parse input arguments."""

    parser = argparse.ArgumentParser(
        description="""
        a simple python script to copy photos from one folder to another
        example: python photo_moving.py --src /home/user/Downloads --dst /home/user/Pictures
        """,
        usage='Use "python . --help" for more information!',
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "-src",
        "--source",
        help="the directory to copy photos from",
        type=str,
    )

    parser.add_argument(
        "-dst",
        "--destination",
        default="./",
        help="the directory to copy photos to, defaults to current directory",
        type=str,
    )

    return parser.parse_args()


def create_folder(folder_path: Path) -> None:
    """Create a folder if it does not exist.

    Args:
        folder_path (str): The folder path.
    """
    if not osp.exists(folder_path):
        os.makedirs(folder_path)


def validate(args: argparse.Namespace) -> tuple[Path, Path]:
    """Validate the input arguments and return the source and destination paths.

    Args:
        args (argparse.Namespace): The parsed arguments.

    Raises:
        ValueError: If no source directory is specified.
        FileNotFoundError: If the source directory does not exist.
        FileNotFoundError: If the destination directory does not exist.

    Returns:
        tuple[Path, Path]: The source and destination paths.
    """
    if args.source is None:
        raise ValueError(
            "Please specify a source directory, e.g. -src /home/user/Downloads"
        )

    if args.destination == "./":
        print("No destination specified, using current directory!")

    src = Path(args.source)
    dst = Path(args.destination)

    if not src.exists():
        raise FileNotFoundError(f"Source {src} does not exist")

    if not dst.exists():
        raise FileNotFoundError(f"Destination {dst} does not exist")

    return src, dst


def copy_photo(file: Path, root: Path, dst: Path) -> None:
    """Copy a photo from one path to another.

    Args:
        file (Path): The file to copy.
        root (Path): The root directory.
        dst (Path): The destination directory.
    """
    # print(f"Found {file} in {root}")

    participant, theme = Path(file.parts[-3]), Path(file.parts[-2])

    create_folder(dst / theme)

    src_file = osp.join(root, file)
    dst_file = osp.join(dst, f"{theme}/{participant}_{file.name}")

    shutil.copy2(src_file, dst_file)


def copy_all_photos(args: argparse.Namespace) -> None:
    """Copy photos from one folder to another.

    Args:
        args (argparse.Namespace): The parsed arguments.
    """
    # Check if the source and destination paths are valid
    src, dst = validate(args)

    # Main loops
    for root, dirs, files in os.walk(src):
        root = Path(root)

        for file in tqdm(files):
            file = Path(file)

            if file.suffix in {".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".gif"}:
                copy_photo(root, file, dst)


if __name__ == "__main__":
    args = parse_args()
    copy_all_photos(args)
