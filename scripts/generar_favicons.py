"""Regenera favicons en static/ desde static/favicon-source/favicon-source.png."""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'static' / 'favicon-source' / 'favicon-source.png'
STATIC = ROOT / 'static'


def main():
    if not SOURCE.exists():
        raise SystemExit(
            f'Falta el archivo fuente: {SOURCE}\n'
            'Sube un PNG cuadrado de 512x512 px con ese nombre.'
        )

    base = Image.open(SOURCE).convert('RGBA')
    base = base.resize((512, 512), Image.Resampling.LANCZOS)

    img32 = base.resize((32, 32), Image.Resampling.LANCZOS)
    img180 = base.resize((180, 180), Image.Resampling.LANCZOS)

    img32.save(STATIC / 'favicon-32x32.png', format='PNG')
    img180.save(STATIC / 'apple-touch-icon.png', format='PNG')
    img32.save(STATIC / 'favicon.ico', format='ICO', sizes=[(32, 32), (48, 48)])

    print('Favicons actualizados en static/')


if __name__ == '__main__':
    main()
