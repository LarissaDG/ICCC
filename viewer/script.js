let data = [];
let currentIndex = 0;

async function loadAllCSVs() {

  const csvOriginal = "https://raw.githubusercontent.com/LarissaDG/ICCC/main/dataset/metadata/sampled_SMALL_with_gen_scored.csv";
  const csvSmall    = "https://raw.githubusercontent.com/LarissaDG/ICCC/main/dataset/metadata/sampled_SMALL_with_gen_scored.csv";
  const csvBig      = "https://raw.githubusercontent.com/LarissaDG/ICCC/main/dataset/metadata/sampled_BIG_with_gen_scored.csv";

  // Bases das imagens
  const originalBase = "https://raw.githubusercontent.com/LarissaDG/ICCC/main/APDDv2images/";
  const smallBase    = "https://raw.githubusercontent.com/LarissaDG/ICCC/main/dataset/images/generated_oficial_small/";
  const bigBase      = "https://raw.githubusercontent.com/LarissaDG/ICCC/main/dataset/images/generated_oficial_big/";

  // Função auxiliar para carregar um CSV
  async function loadCSV(url) {
    return new Promise(resolve => {
      Papa.parse(url, {
        download: true,
        header: true,
        skipEmptyLines: "greedy",
        complete: results => resolve(results.data)
      });
    });
  }

  console.log("Carregando CSVs…");

  const [origData, smallData, bigData] = await Promise.all([
    loadCSV(csvOriginal),
    loadCSV(csvSmall),
    loadCSV(csvBig)
  ]);

  console.log("Original:", origData[0]);
  console.log("Small:", smallData[0]);
  console.log("Big:", bigData[0]);

  // Construir o dataset unificado
  const length = Math.min(origData.length, smallData.length, bigData.length);

  data = [];

  for (let i = 0; i < length; i++) {
    const orig = origData[i];
    const sml  = smallData[i];
    const big  = bigData[i];

    if (!orig || !sml || !big) continue;

    const originalFile = String(orig.filename || orig.generated_filename || "").split(/[\\/]/).pop();
    const smallFile    = String(sml.generated_filename || "").split(/[\\/]/).pop();
    const bigFile      = String(big.generated_filename  || "").split(/[\\/]/).pop();

    data.push({
      original: originalBase + originalFile,
      small: smallBase + smallFile,
      big: bigBase + bigFile,
      description: sml.Description || big.Description || "Sem descrição disponível"
    });
  }

  currentIndex = 0;
  updateCarousel();
}

function updateCarousel() {
  const imgOrig = document.getElementById("image-original");
  const imgSmall = document.getElementById("image-small");
  const imgBig   = document.getElementById("image-big");
  const desc     = document.getElementById("image-description");
  const progress = document.getElementById("progress");

  if (data.length === 0) {
    desc.textContent = "Nenhuma imagem disponível.";
    progress.textContent = "0 / 0";
    return;
  }

  const item = data[currentIndex];

  imgOrig.src  = item.original;
  imgSmall.src = item.small;
  imgBig.src   = item.big;
  desc.textContent = item.description;

  progress.textContent = `${currentIndex + 1} / ${data.length}`;
}

function showNext() {
  currentIndex = (currentIndex + 1) % data.length;
  updateCarousel();
}

function showPrev() {
  currentIndex = (currentIndex - 1 + data.length) % data.length;
  updateCarousel();
}

document.getElementById("next-btn").addEventListener("click", showNext);
document.getElementById("prev-btn").addEventListener("click", showPrev);

loadAllCSVs();
