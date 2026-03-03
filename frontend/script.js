// =====================
// Utils
// =====================
function $(id) {
  return document.getElementById(id);
}
function wait(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

// =====================
// LOGIN (index.html)
// =====================
function login() {
  const usuario = $("usuario");
  const senha = $("senha");

  const u = usuario ? usuario.value.trim() : "";
  const s = senha ? senha.value.trim() : "";

  if (!u || !s) {
    alert("Preencha usuário e senha");
    return;
  }

  localStorage.setItem("usuarioLogado", u);
  window.location.href = "feed.html";
}

// =====================
// FEED (feed.html)
// =====================
function buscarPerfil() {
  const search = $("search");
  const nome = search ? search.value.trim() : "";

  if (!nome) {
    alert("Digite um perfil");
    return;
  }

  localStorage.setItem("perfilSelecionado", nome);
  window.location.href = "profile.html";
}

async function carregarTargets() {
  // targets.json fica na pasta frontend/
  const resp = await fetch("targets.json", { cache: "no-store" });
  if (!resp.ok) {
    throw new Error("Não consegui carregar targets.json");
  }
  return await resp.json(); // { perfis: [...], links: [...] }
}

async function rodarAutomatico() {
  let data;
  try {
    data = await carregarTargets();
  } catch (e) {
    alert("Erro ao carregar targets.json. Confira se o servidor está rodando.");
    console.error(e);
    return;
  }

  const perfis = Array.isArray(data.perfis) ? data.perfis : [];
  if (!perfis.length) {
    alert("targets.json não tem perfis.");
    return;
  }

  localStorage.setItem("filaPerfis", JSON.stringify(perfis));
  localStorage.setItem("modoAuto", "1");
  localStorage.setItem("perfilSelecionado", perfis[0]);

  window.location.href = "profile.html";
}

// =====================
// PROFILE (profile.html)
// - Preenche @usuario
// - Modais “...” e denúncia
// - Modo automático
// =====================

// Elementos (podem não existir em todas as páginas)
const overlay = $("overlay");
const menuSheet = $("menuSheet");
const reportSheet = $("reportSheet");

function show(el) {
  if (!overlay || !el) return;
  overlay.classList.remove("hidden");
  el.classList.remove("hidden");
}

function hide(el) {
  if (!el) return;
  el.classList.add("hidden");
}

function closeAll() {
  if (overlay) overlay.classList.add("hidden");
  hide(menuSheet);
  hide(reportSheet);
}

function openMenu() {
  hide(reportSheet);
  show(menuSheet);
}

function openReport() {
  hide(menuSheet);
  show(reportSheet);
}

function backToMenu() {
  hide(reportSheet);
  show(menuSheet);
}

function fakeAction(action) {
  alert(`${action} (simulado)`);
  closeAll();
}

function fakeReport(reason) {
  // fecha modais
  closeAll();

  const toast = $("successToast");
  if (!toast) return;

  toast.classList.remove("hidden");

  setTimeout(() => {
    toast.classList.add("hidden");
  }, 2000);
}

function goFeed() {
  window.location.href = "feed.html";
}

// =====================
// Auto-preencher @usuario e modo automático
// =====================
window.addEventListener("DOMContentLoaded", async () => {
  // Preenche usuário no profile
  const nome = localStorage.getItem("perfilSelecionado");
  if (nome) {
    const title = document.querySelector(".title");
    const handle = document.querySelector(".handle");
    if (title) title.textContent = "@" + nome;
    if (handle) handle.textContent = "@" + nome;
  }

  // Rodar automático somente se estiver no profile.html (tem menuSheet)
  const modoAuto = localStorage.getItem("modoAuto") === "1";
  if (!modoAuto) return;
  if (!menuSheet || !reportSheet) return;

  // fluxo automático: menu → denunciar → spam → ✅ → próximo
  await wait(600);
  openMenu();
  await wait(350);
  openReport();
  await wait(350);

  fakeReport("Spam");

  await wait(2200);
  avancarFila();
});

function avancarFila() {
  const fila = JSON.parse(localStorage.getItem("filaPerfis") || "[]");
  const atual = localStorage.getItem("perfilSelecionado") || "";

  // log no navegador
  const log = JSON.parse(localStorage.getItem("logDenuncias") || "[]");
  if (atual) {
    log.push({
      perfil: atual,
      status: "sucesso",
      data: new Date().toISOString(),
    });
    localStorage.setItem("logDenuncias", JSON.stringify(log));
  }

  // tira o primeiro da fila
  const novaFila = fila.slice(1);
  localStorage.setItem("filaPerfis", JSON.stringify(novaFila));

  if (!novaFila.length) {
    localStorage.removeItem("modoAuto");
    alert("Automático finalizado ✅");
    window.location.href = "feed.html";
    return;
  }

  localStorage.setItem("perfilSelecionado", novaFila[0]);
  window.location.reload(); // carrega próximo perfil no profile.html
}