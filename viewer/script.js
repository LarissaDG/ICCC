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
  image.src = `images/${item.filename.trim()}`;
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

Papa.parse("../dataset/metadata/sampled_BIG_with_gen_scored.csv", {
  download: true,
  header: true,
  complete: function(results) {
    data = results.data.filter(item => item.generated_filename && item.Description);
    updateCarousel();
    console.log(results.data[0]); // veja o que vem no primeiro item
    data = results.data.filter(item => item.generated_filename && item.Description);
    updateCarousel();
  }
});
