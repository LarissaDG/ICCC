let data = [];
let currentIndex = 0;

function loadDataset(version) {
  const csvUrl = version === "BIG"
    ? "https://raw.githubusercontent.com/LarissaDG/ICCC/main/dataset/metadata/sampled_BIG_with_gen_scored.csv"
    : "https://raw.githubusercontent.com/LarissaDG/ICCC/main/dataset/metadata/sampled_SMALL_with_gen_scored.csv";

  Papa.parse(csvUrl, {
    download: true,
    header: true,
    complete: function(results) {
      console.log(`Primeira linha do CSV (${version}):`, results.data[0]);

      data = results.data
        .filter(item => item.generated_filename && item.Description)
        .map(item => {
          const fileName = item.generated_filename.split("/").pop();
          const imageUrl = `https://raw.githubusercontent.com/LarissaDG/ICCC/main/dataset/images/generated_oficial_${version.toLowerCase()}/${fileName}`;
          return {
            image: imageUrl,
            description: item.Description
          };
        });

      currentIndex = 0;
      updateCarousel();
    }
  });
}

function updateCarousel() {
  if (data.length > 0) {
    document.getElementById("carouselImage").src = data[currentIndex].image;
    document.getElementById("carouselDescription").textContent = data[currentIndex].description;
  }
}

// Troca o dataset quando o usuário mudar no select
document.getElementById("datasetSelect").addEventListener("change", function() {
  loadDataset(this.value);
});

// Carrega a versão BIG por padrão ao abrir
loadDataset("BIG");
