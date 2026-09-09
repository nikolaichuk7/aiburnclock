// Cloudflare Pages Function: POST /subscribe  {email, name?, outlet?}
// Adds the address to the Resend press audience. The key is a Pages secret (RESEND_API_KEY).
const AUDIENCE = "a2ae9839-08f6-465e-b20b-549f82a9c5eb";
export async function onRequestPost({ request, env }) {
  let email = "", name = "", outlet = "";
  const ct = request.headers.get("content-type") || "";
  try {
    if (ct.includes("application/json")) { const j = await request.json(); email = j.email || ""; name = j.name || ""; outlet = j.outlet || ""; }
    else { const f = await request.formData(); email = f.get("email") || ""; name = f.get("name") || ""; outlet = f.get("outlet") || ""; }
  } catch (e) { return new Response("bad request", { status: 400 }); }
  email = String(email).trim().toLowerCase();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return new Response("invalid email", { status: 400 });
  const r = await fetch(`https://api.resend.com/audiences/${AUDIENCE}/contacts`, {
    method: "POST", headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({ email, first_name: String(name).slice(0, 80), last_name: String(outlet).slice(0, 80), unsubscribed: false }) });
  if (!r.ok) return new Response("could not subscribe", { status: 502 });
  if (ct.includes("application/json")) return Response.json({ ok: true });
  return Response.redirect("https://aiburnclock.org/press?subscribed=1", 303);
}
export async function onRequestGet() { return Response.redirect("https://aiburnclock.org/press", 302); }
