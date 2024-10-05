//get hash from url
var hash = window.location.hash.substr(1);
//get collection and asset name from hash between &
var collection_name = hash.split('&')[0];
var asset_name = hash.split('&')[1];
var gas = hash.split('&')[2];
console.log(collection_name, asset_name);
document.querySelector('.overlay-stats').style.display = 'block';
fetch(`https://www.amartil.com/mypythonapp/Get_statistics/${collection_name}/${gas}/${asset_name}`)
.then(response => response.text())
.then(data => {
    data += `<style>
                body { margin: 0; height: 100%;}
                </style>`;
    document.getElementById('stats-viewer').srcdoc = data;
    document.querySelector('.overlay-stats').style.display = 'none';
})
.catch(error => {
    console.error('Error fetching data:', error);
    document.querySelector('.overlay-stats').style.display = 'none';
});