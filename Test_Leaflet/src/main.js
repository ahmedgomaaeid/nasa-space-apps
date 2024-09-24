import L from "leaflet";

const STAC_API_URL = "https://earth.gov/ghgcenter/api/stac";
const RASTER_API_URL = "https://earth.gov/ghgcenter/api/raster";

const collection_name = "odiac-ffco2-monthgrid-v2023";

async function fetchData() {
  // const number_of_items = await fetchItemCount(collection_name);
  const response = await fetch(
    `${STAC_API_URL}/collections/${collection_name}/items`
  );
  const items = (await response.json()).features;

  const asset_name = "co2-emissions"; // fossil fuel
  const color_map = "plasma";
  const rescale_values = { max: 450, min: 0 };

  const fetchTile = async (item) => {
    const tileResponse = await fetch(
      `${RASTER_API_URL}/collections/${item.collection}/items/${item.id}/tilejson.json?assets=${asset_name}&color_formula=gamma+r+1.05&colormap_name=${color_map}&rescale=${rescale_values.min},${rescale_values.max}`
    );
    return tileResponse.json();
  };

  const co2_flux_1 = await fetchTile(items[0]);

  return [co2_flux_1];
}

fetchData().then((tiles) => {
  const map1 = L.map("map1").setView([34, -118], 6);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
  }).addTo(map1);
  // Add 2020 layer
  L.tileLayer(
    "https://earth.gov/ghgcenter/api/raster/collections/vulcan-ffco2-yeargrid-v4/items/vulcan-ffco2-yeargrid-v4-2020/tiles/WebMercatorQuad/{z}/{x}/{y}@1x?assets=total-co2&color_formula=gamma+r+1.05&colormap_name=spectral_r&rescale=0%2C450",
    {
      attribution: "GHG",
      opacity: 0.5,
    }
  ).addTo(map1);

  // Add 2019 layer
});
