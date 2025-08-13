let data = [];
let currentIndex = 0;

const smallCSV = "https://raw.githubusercontent.com/LarissaDG/ICCC/main/dataset/metadata/sampled_SMALL_with_gen_scored.csv";
const bigCSV   = "https://raw.githubusercontent.com/LarissaDG/ICCC/main/dataset/metadata/sampled_BIG_with_gen_scored.csv";

const smallBase = "https://raw.githubusercontent.com/LarissaDG/ICCC/main/dataset/images/generated_oficial_small/";
const bigBase   = "https://raw.githubusercontent.com/LarissaDG/ICCC/main/dataset/images/generated_oficial_big/";

function loadDataset() {
  Papa.parse(smallCSV, {
    download: true,
    header: true,
    skipEmptyLines: "greedy",
    complete: function(resultsSmall) {
      const smallData = resultsSmall.data
        .filter(item => item.generated_filename && item.Description)
        .map(item => {
          const fileName = String(item.generated_filename).split(/[\\/]/).pop();
          return {
            filename: fileName,
            small: smallBase + fileName,
            description: String(item.Description).trim(),
            big: null // será preenchido depois
          };
        });

      // Agora carrega o BIG
      Papa.parse(bigCSV, {
        download: true,
        header: true,
        skipEmptyLines: "greedy",
        complete: function(resultsBig) {
          const bigData = resultsBig.data
            .filter(item => item.generated_filename)
            .map(item => {
              const fileName = String(item.generated_filename).split(/[\\/]/).pop();
              return {
                filename: fileName,
                big: bigBase + fileName
              };
            });

          // Mescla os dados pelo filename
          data = smallData.map(smallItem => {
            const bigItem = bigData.find(b => b.filename === smallItem.filename);
            return {
              small: smallItem.small,
              big: bigItem ? bigItem.big : "",
              description: smallItem.description
            };
          });

          currentIndex = 0;
          updateCarousel();
        },
        error: function(err) {
          console.error("Erro ao carregar CSV BIG:", err);
        }
      });
    },
    error: function(err) {
      console.error("Erro ao carregar CSV SMALL:", err);
    }
  });
}

function updateCarousel() {
  const imgSmall = document.getElementById("image-small");
  const imgBig   = document.getElementById("image-big");
  const desc     = document.getElementById("image-description");
  const progress = document.getElementById("progress");

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
  if (data.length === 0) return;
  currentIndex = (currentIndex + 1) % data.length;
  updateCarousel();
}

function showPrev() {
  if (data.length === 0) return;
  currentIndex = (currentIndex - 1 + data.length) % data.length;
  updateCarousel();
}

document.getElementById("next-btn").addEventListener("click", showNext);
document.getElementById("prev-btn").addEventListener("click", showPrev);

loadDataset();
