let data = [];
let currentIndex = 0;

const smallCSV = "https://raw.githubusercontent.com/LarissaDG/ICCC/main/dataset/metadata/sampled_SMALL_with_gen_scored.csv";
const bigCSV   = "https://raw.githubusercontent.com/LarissaDG/ICCC/main/dataset/metadata/sampled_BIG_with_gen_scored.csv";

const smallBase = "https://raw.githubusercontent.com/LarissaDG/ICCC/main/dataset/images/generated_oficial_small/";
const bigBase   = "https://raw.githubusercontent.com/LarissaDG/ICCC/main/dataset/images/generated_oficial_big/";

// helper: Papa.parse com Promise
function parseCSV(url) {
  return new Promise((resolve, reject) => {
    Papa.parse(url, {
      download: true,
      header: true,
      skipEmptyLines: "greedy",
      complete: (res) => resolve(res.data || []),
      error: (err) => reject(err),
    });
  });
}

// extrai o ID numérico do nome do arquivo (funciona para img_small_123.jpg e img_big_123.jpg)
function extractIdFromPath(path) {
  const file = String(path).split(/[\\/]/).pop() || "";
  // tenta padrão img_small_123.jpg ou img_big_123.png etc.
  let m = file.match(/img_(?:small|big)_(\d+)\.(?:jpg|jpeg|png|webp)$/i);
  if (m) return m[1];
  // fallback: pega o último número antes da extensão
  m = file.match(/(\d+)(?=\.(?:jpg|jpeg|png|webp)$)/i);
  return m ? m[1] : null;
}

async function loadDataset() {
  try {
    // carrega ambos ao mesmo tempo
    const [smallRows, bigRows] = await Promise.all([parseCSV(smallCSV), parseCSV(bigCSV)]);

    // monta mapas por ID
    const smallMap = new Map();
    for (const row of smallRows) {
      if (!row.generated_filename || !row.Description) continue;
      const id = extractIdFromPath(row.generated_filename);
      if (!id) continue;
      const fileName = String(row.generated_filename).split(/[\\/]/).pop();
      smallMap.set(id, {
        url: smallBase + fileName,
        desc: String(row.Description).trim(),
      });
    }

    const bigMap = new Map();
    for (const row of bigRows) {
      if (!row.generated_filename) continue;
      const id = extractIdFromPath(row.generated_filename);
      if (!id) continue;
      const fileName = String(row.generated_filename).split(/[\\/]/).pop();
      bigMap.set(id, {
        url: bigBase + fileName,
      });
    }

    // une apenas IDs que existem nos dois (para garantir par completo)
    const ids = [...smallMap.keys()].filter((id) => bigMap.has(id));
    ids.sort((a, b) => Number(a) - Number(b)); // ordena por ID numérica

    data = ids.map((id) => ({
      small: smallMap.get(id).url,
      big: bigMap.get(id).url,
      description: smallMap.get(id).desc, // descrição pode vir do SMALL (ou BIG; são iguais)
    }));

    currentIndex = 0;
    updateCarousel();

    if (data.length === 0) {
      console.warn("Nenhum par SMALL/BIG correspondente encontrado. Verifique os CSVs.");
    } else {
      console.log(`Pares carregados: ${data.length}`);
      console.log("Exemplo:", data[0]);
    }
  } catch (e) {
    console.error("Erro ao carregar datasets:", e);
  }
}

function updateCarousel() {
  const imgSmall = document.getElementById("image-small");
  const imgBig   = document.getElementById("image-big");
  const desc     = document.getElementById("image-description");
  const progress = document.getElementById("progress");

  if (!imgSmall || !imgBig || !desc || !progress) return;

  if (data.length === 0) {
    imgSmall.src = "";
    imgBig.src = "";
    desc.textContent = "Nenhuma imagem disponível.";
    progress.textContent = "0 / 0";
    return;
  }

  const item = data[currentIndex];
  imgSmall.src = item.small;
  imgBig.src   = item.big;
  desc.textContent = item.description;
  progress.textContent = `${currentIndex + 1} / ${data.length}`;
}

function showNext() {
  if (!data.length) return;
  currentIndex = (currentIndex + 1) % data.length;
  updateCarousel();
}

function showPrev() {
  if (!data.length) return;
  currentIndex = (currentIndex - 1 + data.length) % data.length;
  updateCarousel();
}

document.getElementById("next-btn").addEventListener("click", showNext);
document.getElementById("prev-btn").addEventListener("click", showPrev);

// navegação por teclado
window.addEventListener("keydown", (e) => {
  if (e.key === "ArrowRight") showNext();
  if (e.key === "ArrowLeft") showPrev();
});

loadDataset();
