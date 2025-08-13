let data = [];
let currentIndex = 0;

function updateCarousel() {
  const image = document.getElementById('carousel-image');
  const caption = document.getElementById('carousel-caption');
  const progress = document.getElementById('progress');

  if (data.length === 0) {
    caption.textContent = "Nenhuma imagem disponível.";
    progress.textContent = "0 / 0";
    image.src = "";
    image.alt = "";
    return;
  }

  const item = data[currentIndex];
  image.src = item.image; // já vem com a URL completa
  image.alt = item.description;
  caption.textContent = item.description;
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

document.getElementById('next-btn').addEventListener('click', showNext);
document.getElementById('prev-btn').addEventListener('click', showPrev);

// Link RAW do CSV no GitHub
const csvUrl = "https://raw.githubusercontent.com/LarissaDG/ICCC/main/dataset/metadata/sampled_BIG_with_gen_scored.csv";

Papa.parse(csvUrl, {
  download: true,
  header: true,
  complete: function(results) {
    console.log("Primeira linha do CSV:", results.data[0]);

    data = results.data
      .filter(item => item.generated_filename && item.Description)
      .map(item => {
        const fileName = item.generated_filename.split("/").pop(); // pega só o nome do arquivo
        const imageUrl = `https://raw.githubusercontent.com/LarissaDG/ICCC/main/dataset/images/generated_oficial_big/${fileName}`;
        return {
          image: imageUrl,
          description: item.Description
        };
      });

    updateCarousel();
  }
});
