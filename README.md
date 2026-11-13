# ZYTHON

ZYTHON: o'z sintaksisiga ega, noldan yozilgan dasturlash tili.
Hozirgi versiya: **0.1.0**

## Hozir ishlaydi

- Lexer, recursive-descent parser, AST
- Interpretator: o'zgaruvchilar, konstantalar, funksiyalar, yopilishlar (closures), rekursiya
- `if`, `while`, `for ... in`, `break`, `continue`
- Massivlar, lug'atlar, satr va son operatsiyalari
- Xato xabarlari: fayl, qator, ustun, tavsif va yechim
- Bajarish chegaralari: qadamlar soni, chaqiruv chuqurligi, chiqish hajmi
- CLI (`run`, `repl`, `test`) va HTTP server

## Hali yo'q

Bytecode VM, GC, sinflar, modullar, type checker, paket menejeri, web/bot/DB frameworklari.

## Lokal ishlatish

```bash
python zython.py test
python zython.py run app.zy
python zython.py repl

pip install -r requirements.txt
python server.py
```

## Misol dastur

```zython
let name = "ZYTHON"
fn add(a, b) { return a + b }
print("Hello, " + name + " " + str(add(10, 20)))
```

## API

```bash
curl https://SIZNING-XIZMAT.onrender.com/health

curl -X POST https://SIZNING-XIZMAT.onrender.com/run \
  -H "Content-Type: application/json" \
  -d '{"source": "print(1 + 2 * 3)"}'
```

Javob:

```json
{"ok": true, "output": "7\n", "steps": 7}
```

Xato bo'lsa `ok` `false` bo'ladi va `error` ichida `line`, `col`, `message`, `hint` qaytadi.

## Xavfsizlik haqida

Hozirgi versiya tilning o'zi xavfli tizim funksiyalarini (fayl, tarmoq, OS) bermaydi, lekin u hali alohida sandbox emas. Serverda kod qadamlar soni, chiqish hajmi va chaqiruv chuqurligi bilan cheklangan. Ishonchsiz foydalanuvchilar uchun keyingi bosqichda process yoki container izolyatsiyasi kerak.

## Litsenziya

MIT
