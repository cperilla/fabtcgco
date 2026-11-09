"""Composición editable del lanzamiento: recursos originales, texto y QR."""
from pathlib import Path
import base64

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent

def asset(path, mime):
    return f'data:{mime};base64,' + base64.b64encode(Path(path).read_bytes()).decode()

def make_launch():
    shinsei = asset(ROOT / 'public/images/stores/shinsei.png', 'image/png')
    fabco = asset(ROOT / 'public/images/FABLogo.png', 'image/png')
    fab = asset(ROOT / 'public/images/print/fab-logo-official-trimmed.png', 'image/png')
    font = asset('/usr/share/fonts/TTF/AlbertSans[wght].ttf', 'font/ttf')
    qr = asset(OUT / 'mesa-inicial-qr.png', 'image/png')
    slv = asset(ROOT / 'public/images/shinsei/silver-age.webp', 'image/webp')
    omens = asset(ROOT / 'public/images/shinsei/omens/logo.webp', 'image/webp')
    heroes = [asset(ROOT / f'output/shinsei/materiales/{name}', 'image/jpeg') for name in ['OMN_art_sig_aurora_adult-402x560.jpg', 'OMN_art_sig_oscilio_young-402x560.jpg', 'OMN_art_sig_zyggy_adult-402x560.jpg']]
    products = [asset(ROOT / f'output/shinsei/materiales/precons/{name}.webp', 'image/webp') for name in ['chapter-one', 'prism', 'viserai']]
    css = '''
@font-face{font-family:Albert;src:url("FONT");font-weight:100 900}
*{box-sizing:border-box}html,body{margin:0;width:1080px;height:1350px}body{font-family:Albert,Arial,sans-serif;color:#30203f;background:#efd6e9}main{width:1080px;height:1350px;overflow:hidden}
header{height:132px;padding:14px 48px;display:flex;align-items:center;justify-content:space-between;background:#efd6e9}.host{display:flex;align-items:center;gap:17px}.host img{width:99px;height:102px;object-fit:contain}.host span{font-size:17px;letter-spacing:2px}.host b{font-size:27px;letter-spacing:0;display:block}.fab{width:190px;height:100px;object-fit:contain}.co{display:flex;align-items:center;gap:10px;font-size:17px;font-weight:700}.co img{height:100px;width:100px;object-fit:contain}
.hero{height:420px;position:relative;background:#352044;overflow:hidden;color:#fff3f4}.collage{display:grid;grid-template-columns:repeat(3,1fr);position:absolute;inset:0}.collage img{width:100%;height:100%;object-fit:cover;object-position:center 32%;min-width:0}.shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(35,16,55,.75),transparent 25%,transparent 47%,rgba(36,18,53,.94) 99%)}.eyebrow{position:absolute;top:18px;left:48px;margin:0;font-size:28px;font-weight:700;color:#fff0fa}.hero h1{position:absolute;bottom:20px;left:48px;font-size:64px;line-height:1.02;letter-spacing:-2px;font-weight:900;margin:0;text-transform:uppercase}.hero h1 em{font-style:normal;color:#f0bedf}
.format{height:130px;padding:20px 48px;background:#392447;display:flex;align-items:center;justify-content:space-between;color:#fff0fa;gap:38px}.format img{width:550px;height:auto;flex-shrink:0}.format p{font-size:23px;line-height:1.15;margin:0;padding-left:25px;border-left:1px solid #bfa0cc}.format strong{display:block;font-size:27px;margin-bottom:5px}
.prizes{height:95px;padding:9px 48px;background:#d7c2e5;display:flex;align-items:center;justify-content:space-between;gap:28px}.prizes p{font-size:29px;font-weight:750;letter-spacing:-.5px;margin:0;line-height:1.15}.prizes img{width:235px;height:78px;object-fit:contain}.precons{height:150px;display:flex;align-items:center;padding:8px 48px;gap:15px;background:#f6e9f0}.precons p{font-size:24px;line-height:1.2;margin:0;width:320px;flex-shrink:0}.precons b{display:block;font-size:27px;margin-bottom:7px}.products{display:flex;flex:1;min-width:0;align-items:center;justify-content:flex-end;gap:13px;height:100%}.products img{width:76px;height:130px;object-fit:contain;flex:0 0 76px}.products .lineup{width:auto;min-width:0;height:142px;object-fit:contain;flex:1 1 0}
.info{height:145px;padding:20px 48px;background:#efd6e9;display:flex;align-items:center;justify-content:space-between}.info h2{font-size:46px;letter-spacing:-1.5px;margin:0 0 9px;line-height:1}.info p{font-size:25px;margin:0;line-height:1.3}.address{text-align:right}.address b{font-size:31px;display:block;margin-bottom:7px}.address p{font-size:26px}
.cta{height:228px;background:#392447;color:#fff3f4;padding:23px 48px;position:relative}.cta .small{font-size:24px;margin:0 0 7px;color:#ead4ee}.cta h2{font-size:43px;letter-spacing:-1px;line-height:1;margin:0 0 12px}.cta p{font-size:24px;line-height:1.3;margin:0;max-width:735px}.cta a{display:block;font-size:25px;color:#f3c6e4;text-decoration:none;font-weight:750;margin-top:12px}.qr{position:absolute;right:48px;top:35px;width:152px;height:152px}.foot{height:50px;padding:14px 48px;display:flex;justify-content:space-between;align-items:center;font-size:18px;background:#efd6e9}.foot b{font-size:20px}
/* Adaptaciones de composición: mantienen el texto legible, sin recortar la pieza. */
.square{height:1080px}.square header{height:112px}.square .host img{width:82px;height:85px}.square .co img{width:82px;height:85px}.square .fab{width:170px;height:90px}.square .hero{height:305px}.square .collage img{object-position:center 26%}.square .eyebrow{font-size:25px;top:14px}.square .hero h1{font-size:52px;bottom:15px}.square .format{height:103px}.square .format img{width:495px}.square .format p{font-size:23px}.square .prizes{height:76px}.square .prizes img{height:65px;width:215px}.square .prizes p{font-size:27px}.square .precons{height:117px}.square .products img{height:105px;width:61px;flex-basis:61px}.square .products .lineup{height:110px;width:405px}.square .precons p{font-size:22px}.square .precons b{font-size:24px}.square .info{height:126px}.square .info h2{font-size:42px}.square .info p{font-size:23px}.square .cta{height:197px;padding-top:17px}.square .cta h2{font-size:38px}.square .cta p{font-size:23px}.square .cta .small{font-size:22px}.square .cta a{font-size:23px;margin-top:10px}.square .qr{width:136px;height:136px;top:30px}.square .foot{height:44px;font-size:17px}
.story{height:1920px}.story header{height:210px;padding-top:65px}.story .hero{height:690px}.story .collage img{object-position:center center}.story .eyebrow{top:30px;font-size:31px}.story .hero h1{font-size:82px;bottom:45px}.story .format{height:145px}.story .prizes{height:110px}.story .precons{height:190px}.story .products .lineup{height:180px}.story .products img{height:165px;width:90px;flex-basis:90px}.story .info{height:175px}.story .cta{height:290px;padding-top:45px}.story .cta h2{font-size:47px}.story .cta p{font-size:26px}.story .cta .small{font-size:27px}.story .qr{top:65px;width:163px;height:163px}.story .foot{height:110px;padding-bottom:55px}
'''.replace('FONT', font)
    css += '''
.print{height:1527px}.print header{height:150px}.print .hero{height:470px}.print .format{height:140px}.print .prizes{height:110px}.print .precons{height:175px}.print .info{height:155px}.print .cta{height:267px}.print .foot{height:60px}
@page{size:A3;margin:0}@media print{html,body{width:297mm;height:420mm;margin:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}main.print{zoom:1.03937007874}}
'''
    collage = ''.join(f'<img src="{src}" alt="{name}">' for src, name in zip(heroes, ['Aurora', 'Oscilio', 'Zyggy']))
    product_html = ''.join(f'<img class="{cl}" src="{src}" alt="{name}">' for src, name, cl in zip(products, ['Preconstruidos Silver Age: Dash, Bravo, Iyslander, Kayo y Viserai', 'Prism, Advent of Thrones', 'Viserai, Between Worlds'], ['lineup', '', '']))
    for name, variant, height in [('afiche-tienda', 'print', 1527)]:
        html = f'''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=1080"><title>Silver Age en Shinsei · Omens of the Third Age</title><style>{css}html,body{{height:{height}px}}</style><main class="{variant}">
<header><div class="host"><img src="{shinsei}" alt="Shinsei Store"><span>JUGAMOS EN<b>Shinsei Store</b>CALI</span></div><img class="fab" src="{fab}" alt="Flesh and Blood"><div class="co">Con la<br>comunidad<img src="{fabco}" alt="FAB Colombia"></div></header>
<section class="hero"><div class="collage">{collage}</div><div class="shade"></div><p class="eyebrow">¿Ya juegas TCG? Descubre Flesh and Blood.</p><h1>Tu próxima batalla<br><em>empieza aquí.</em></h1></section>
<section class="format"><img src="{slv}" alt="Silver Age"><p><strong>Empieza a competir.</strong>Mazos accesibles.<br>Estrategia en cada partida.</p></section>
<section class="prizes"><p>Premios del set<br>Omens of the Third Age</p><img src="{omens}" alt="Omens of the Third Age"></section>
<section class="precons"><p><b>Tu primer mazo.</b>Conoce los preconstruidos<br>de Silver Age.</p><div class="products">{product_html}</div></section>
<section class="info"><div><h2>Jueves · 5 p. m.</h2><p><b>Todos los jueves</b><br>Ven a jugar con FAB Colombia.</p></div><div class="address"><b>Shinsei Store</b><p>Cra. 52B #18-40 · Cali</p></div></section>
<section class="cta"><p class="small">¿Quieres prepararte o aprender a jugar?</p><h2>Únete a Mesa Inicial →</h2><p>Podemos enseñarte y prestarte un mazo ese día.<br><b>Avísanos con anticipación para coordinar.</b></p><a href="https://fabtcgcolombia.club/mesa-inicial">fabtcgcolombia.club/mesa-inicial</a><img class="qr" src="{qr}" alt="Escanea para unirte a Mesa Inicial"></section>
<footer class="foot"><b>FAB Colombia × Shinsei Store</b><span>Aprende, juega y compite.</span></footer>
</main></html>'''
        (OUT / f'{name}.html').write_text(html)

    # Instagram: tres cuadrados, información repartida y un héroe por pieza. Sin QR.
    carousel_css = '''
@font-face{font-family:Albert;src:url("FONT");font-weight:100 900}*{box-sizing:border-box}html,body{margin:0;width:1080px;height:1080px}body{font-family:Albert,Arial,sans-serif;background:#efd6e9;color:#30203f}main{width:1080px;height:1080px;overflow:hidden;position:relative}
header{height:112px;display:flex;align-items:center;justify-content:space-between;padding:12px 48px;background:#efd6e9}.host{display:flex;align-items:center;gap:16px}.host img{width:83px;height:86px;object-fit:contain}.host span{font-size:17px;letter-spacing:2px}.host b{display:block;font-size:27px;letter-spacing:0}.fab{width:175px;height:90px;object-fit:contain}.co{display:flex;align-items:center;gap:8px;font-size:16px;font-weight:700}.co img{width:83px;height:86px;object-fit:contain}
.hero{height:650px;position:relative;background:#342047;color:#fff3fa;overflow:hidden}.hero-art{position:absolute;right:0;top:-10px;width:660px;height:740px;object-fit:cover;object-position:center 32%}.shade{position:absolute;inset:0;background:linear-gradient(90deg,#342047 0%,rgba(52,32,71,.94) 26%,rgba(52,32,71,.35) 53%,rgba(52,32,71,0) 76%),linear-gradient(0deg,#342047,transparent 25%)}.eyebrow{position:absolute;left:48px;top:29px;margin:0;font-size:27px;font-weight:650;color:#f5d6ec}.hero h1{position:absolute;left:48px;top:100px;margin:0;font-size:84px;line-height:.98;letter-spacing:-3px;font-weight:900;text-transform:uppercase}.hero h1 em{font-style:normal;color:#efbedf}.silver{position:absolute;left:48px;bottom:30px;width:600px;height:auto}.counter{position:absolute;right:48px;bottom:35px;font-size:24px;color:#f4d7ed;letter-spacing:2px;font-weight:600}
.details{height:318px;background:#efd6e9;padding:27px 48px;position:relative}.details p{font-size:29px;line-height:1.25;margin:0 0 14px}.details strong{font-weight:800}.when{display:flex;justify-content:space-between;align-items:center;margin-bottom:21px}.when strong{font-size:65px;letter-spacing:-2px;line-height:1}.when p{text-align:right;font-size:29px;margin:0}.when b{display:block;font-size:33px;margin-bottom:5px}.details .recurrence{font-size:27px;line-height:1.35}.details .exception{font-size:23px;margin-top:12px}.details h2{font-size:39px;font-weight:800;letter-spacing:-1px;line-height:1.1;margin:0 0 14px}.details .prizes{display:flex;align-items:center;justify-content:space-between;gap:20px;margin-top:20px}.prizes p{font-size:27px;margin:0}.prizes img{width:225px;height:86px;object-fit:contain}.second h1{font-size:78px;top:105px}.third h1{font-size:81px;top:105px}.third .hero-art{width:640px;height:740px;top:-40px;object-position:center 28%}.third .details{background:#d7c2e5}.third .details p{font-size:28px}.details .url{display:block;font-size:27px;font-weight:800;color:#392447;text-decoration:none;margin:20px 0 0}.details .closing{font-size:24px;margin-top:18px}
'''.replace('FONT', font)
    carousel_css += """
/* Full-bleed artwork; light lilac is limited to text and small accents. */
body{background:#120e1e;color:#fff3fa}main{background:#120e1e;color:#fff3fa}
main>.hero-art,main.third>.hero-art{position:absolute;right:-50px;top:-55px;width:900px;height:1254px;object-fit:cover;object-position:center;z-index:0;mask-image:linear-gradient(90deg,transparent,#000 15%)}
main>.shade{position:absolute;inset:0;z-index:1;background:linear-gradient(90deg,rgba(18,14,30,.96) 0%,rgba(18,14,30,.76) 25%,rgba(18,14,30,.15) 60%,transparent 82%),linear-gradient(0deg,#120e1e 0%,rgba(18,14,30,.93) 23%,transparent 60%),linear-gradient(180deg,rgba(18,14,30,.65),transparent 18%)}
header,.hero,.details{position:relative;z-index:2;background:transparent}.third .details{background:transparent}
header{color:#fff3fa}.host span{color:#d7c2e5}.host b{color:#fff3fa}.hero{overflow:visible}.details{color:#fff3fa}
.hero h1 em,.details h2,.details .url,.counter{color:#d7c2e5}.details .exception{color:#d7c2e5}
"""
    carousel = [
        ('instagram-01-aurora', '', heroes[0], 'Aurora', '¿Ya juegas TCG? Descubre Flesh and Blood.', 'Este jueves<br>jugamos<br><em>en Shinsei.</em>', '''<div class="when"><strong>5 p. m.</strong><p><b>Shinsei Store</b>Cra. 52B #18-40 · Cali</p></div><p class="recurrence">Desde el <strong>12 de noviembre de 2026.</strong><br>Todos los jueves con FAB Colombia.</p><p class="exception">Sin actividad el 24 y 31 de diciembre.</p>'''),
        ('instagram-02-oscilio', 'second', heroes[1], 'Oscilio', 'Silver Age · Flesh and Blood', 'Entra al<br>juego<br><em>competitivo.</em>', f'''<h2>Mazos accesibles. Estrategia real.</h2><p>Conoce los mazos preconstruidos de Silver Age.<br>Aprende estrategias y juega con la comunidad.</p><div class="prizes"><p><strong>Premios del set</strong><br>Omens of the Third Age.</p><img src="{omens}" alt="Omens of the Third Age"></div>'''),
        ('instagram-03-zyggy', 'third', heroes[2], 'Zyggy', 'Tu primera partida empieza con la comunidad.', '¿Primera<br>partida?<br><em>Mesa Inicial.</em>', '''<h2>Únete a Mesa Inicial →</h2><p>Podemos enseñarte y prestarte un mazo ese día.<br><strong>Avísanos con anticipación para coordinar.</strong></p><a class="url" href="https://fabtcgcolombia.club/mesa-inicial">fabtcgcolombia.club/mesa-inicial</a><p class="closing">Ven a jugar este jueves · Shinsei Store · 5 p. m.</p>'''),
    ]
    for index, (name, variant, art, hero_name, eyebrow, headline, details) in enumerate(carousel, 1):
        html = f'''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=1080"><title>Shinsei · Instagram {index} · {hero_name}</title><style>{carousel_css}</style><main class="{variant}">
<img class="hero-art" src="{art}" alt="{hero_name}, arte de Omens of the Third Age"><div class="shade"></div>
<header><div class="host"><img src="{shinsei}" alt="Shinsei Store"><span>JUGAMOS EN<b>Shinsei Store</b>CALI</span></div><img class="fab" src="{fab}" alt="Flesh and Blood"><div class="co">Con la<br>comunidad<img src="{fabco}" alt="FAB Colombia"></div></header>
<section class="hero"><p class="eyebrow">{eyebrow}</p><h1>{headline}</h1><img class="silver" src="{slv}" alt="Silver Age"><span class="counter">{index} / 3</span></section>
<section class="details">{details}</section></main></html>'''
        (OUT / f'{name}.html').write_text(html)


if __name__ == '__main__':
    make_launch()
