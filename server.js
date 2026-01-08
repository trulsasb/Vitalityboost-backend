
/*****************************************************************
 * VITALITY BOOST – PRODUKSJON BACKEND
 * Node.js + Express + SQLite + Stripe + Admin
 *****************************************************************/

const express = require("express");
const session = require("express-session");
const rateLimit = require("express-rate-limit");
const sqlite3 = require("sqlite3").verbose();
const { createObjectCsvWriter } = require("csv-writer");
const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY || "sk_test_dummy");

const app = express();

/* ---------------- MIDDLEWARE ---------------- */
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(
  rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 300,
  })
);

app.use(
  session({
    secret: "vitalityboost_admin_secret",
    resave: false,
    saveUninitialized: false,
  })
);

/* ---------------- DATABASE ---------------- */
const db = new sqlite3.Database("./database.db");

db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      title TEXT,
      price INTEGER,
      active INTEGER,
      stock INTEGER
    )
  `);

  db.run(`
    CREATE TABLE IF NOT EXISTS orders (
      id TEXT PRIMARY KEY,
      email TEXT,
      amount INTEGER,
      method TEXT,
      status TEXT,
      created DATETIME
    )
  `);

  db.run(`
    CREATE TABLE IF NOT EXISTS admins (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE,
      password TEXT
    )
  `);

  // Seed produkter hvis tom
  db.get("SELECT COUNT(*) AS count FROM products", (err, row) => {
    if (row && row.count === 0) {
      const stmt = db.prepare(
        "INSERT INTO products (title, price, active, stock) VALUES (?,?,?,?)"
      );
      stmt.run("Omega Vital+", 399, 1, 20);
      stmt.run("Collagen Boost 50+", 449, 1, 15);
      stmt.run("MindSharp Focus", 349, 1, 25);
      stmt.run("Longevity Multivitamin", 299, 1, 30);
      stmt.finalize();
    }
  });
});

/* ---------------- AUTH ---------------- */
function requireAdmin(req, res, next) {
  if (req.session.admin) return next();
  res.redirect("/admin/login");
}

/* ---------------- ADMIN LOGIN ---------------- */
app.get("/admin/login", (req, res) => {
  res.send(`
    <h2>Admin Login</h2>
    <form method="POST">
      <input name="username" placeholder="Brukernavn" /><br/>
      <input name="password" type="password" placeholder="Passord" /><br/>
      <button>Logg inn</button>
    </form>
  `);
});

app.post("/admin/login", (req, res) => {
  const { username, password } = req.body;
  db.get(
    "SELECT * FROM admins WHERE username=? AND password=?",
    [username, password],
    (err, row) => {
      if (row) {
        req.session.admin = { id: row.id, username: row.username };
        res.redirect("/admin");
      } else {
        res.send("Feil brukernavn eller passord");
      }
    }
  );
});

/* ---------------- ADMIN DASHBOARD ---------------- */
app.get("/admin", requireAdmin, (req, res) => {
  db.all("SELECT * FROM orders", (err, orders) => {
    db.all("SELECT * FROM products", (err, products) => {
      const total = orders.reduce((s, o) => s + o.amount, 0);

      res.send(`
<!DOCTYPE html>
<html>
<body style="font-family:system-ui;padding:1rem">
<h1>Admin Dashboard</h1>
<p>Ordrer: ${orders.length} | Omsetning: ${total} kr</p>

<h2>Produkter</h2>
<table border="1" cellpadding="5">
<tr><th>ID</th><th>Tittel</th><th>Pris</th><th>Lager</th></tr>
${products
  .map(
    (p) =>
      `<tr><td>${p.id}</td><td>${p.title}</td><td>${p.price}</td><td>${p.stock}</td></tr>`
  )
  .join("")}
</table>

<p><a href="/admin/logout">Logg ut</a></p>
</body>
</html>
      `);
    });
  });
});

app.get("/admin/logout", (req, res) => {
  req.session.destroy(() => res.redirect("/admin/login"));
});

/* ---------------- ORDRE ---------------- */
app.post("/order", (req, res) => {
  const { email, amount } = req.body;
  const orderId = "ORD-" + Date.now();

  db.run(
    "INSERT INTO orders VALUES (?,?,?,?,?,?)",
    [orderId, email, amount, "PENDING", "PENDING", new Date().toISOString()],
    () => res.json({ ok: true, orderId })
  );
});

/* ---------------- FRONTEND ---------------- */
app.get("/", (req, res) => {
  db.all("SELECT * FROM products WHERE active=1", (err, products) => {
    res.send(`
<h1>Vitality Boost</h1>
<ul>
${products
  .map((p) => `<li>${p.title} – ${p.price} kr (Lager: ${p.stock})</li>`)
  .join("")}
</ul>
    `);
  });
});

/* ---------------- START SERVER ---------------- */
const PORT = process.env.PORT || 3000;
app.listen(PORT, () =>
  console.log("🚀 Vitality Boost server kjører på port", PORT)

);
