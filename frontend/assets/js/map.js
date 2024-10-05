// Fetch and display the initial map
fetch('../../output.html')
    .then(response => response.text())
    .then(data => {
        document.getElementById('map-viewer').srcdoc = data;
    })
    .catch(error => {
        console.error('Error fetching data:', error);
    });

// IDs of the select elements in order
const selectedIds = ['type', 'gas', 'about', 'collection_name', 'year', 'month', 'day'];
let jsonData = {};

function getUrlHashParam() {
    var hash = window.location.hash;
    hash = hash.slice(1);
    if(hash == 'human'){
        document.getElementById('type').value = "Human Cause";
        onSelectChange(0);
    }else if(hash == "natural"){
        document.getElementById('type').value = "Natural Cause";
        onSelectChange(0);
    }else if(hash == "larg")
    {
        document.getElementById('type').value = "Large Emission Events";
        onSelectChange(0);
    }
}


//function to hide select elements starting from a certain index
function hideLowerSelects(startIndex) {
    for (let i = startIndex; i < selectedIds.length; i++) {
        const elem = document.getElementById(selectedIds[i]);
        if (elem) {
            elem.style.display = 'none';
            elem.style.borderTop = '';
            elem.value = '';
        }
    }
}

// Function to populate a select element with options
function populateSelect(selectId, options, defaultOptionText) {
    const selectElem = document.getElementById(selectId);
    if (!selectElem || !options) return;
    selectElem.innerHTML = `<option selected disabled>${defaultOptionText}</option>`;
    if (Array.isArray(options)) {
        // Handle array options (for 'collection_name')
        options.forEach((item, index) => {
            const optionText = item.text || item.collection_name || `Option ${index}`;
            selectElem.innerHTML += `<option value="${index}">${optionText}</option>`;
        });
    } else if (typeof options === 'object') {
        // Handle object options
        for (let key in options) {
            const optionText = options[key].text || key;
            selectElem.innerHTML += `<option value="${key}">${optionText}</option>`;
        }
    }
    selectElem.style.display = 'inline-block';
    selectElem.style.borderTop = '2px solid #37517e';
}

// Function to get selected values up to a certain level
function getSelectedValues(level) {
    const values = {};
    for (let i = 0; i <= level; i++) {
        const selectId = selectedIds[i];
        const selectElem = document.getElementById(selectId);
        if (selectElem) {
            values[selectId] = selectElem.value;
        }
    }
    return values;
}

function open_filter_bar()
{
    document.getElementById('filter-bar').style.display = 'block';
}
function close_filter_bar()
{
    document.getElementById('filter-bar').style.display = 'none';
}
// Function to get options for the next select based on selected values
function getNextOptions(level) {
    let data = jsonData;
    for (let i = 0; i <= level; i++) {
        const selectId = selectedIds[i];
        const selectValue = document.getElementById(selectId).value;
        data = data[selectValue];
        if (!data) break;
    }
    return data;
}

// Function to handle select change events
function onSelectChange(level) {
    hideLowerSelects(level + 1);
    const selectElem = document.getElementById(selectedIds[level]);
    selectElem.style.borderTop = '2px solid green';

    if (level < 3) {
        // For 'type', 'gas', 'about', populate next select
        const nextOptions = getNextOptions(level);
        if (nextOptions) {
            const nextSelectId = selectedIds[level + 1];
            let defaultOptionText = '';
            switch (nextSelectId) {
                case 'gas':
                    defaultOptionText = 'Choose Type Of Gas...';
                    break;
                case 'about':
                    defaultOptionText = 'Choose Study...';
                    break;
                case 'collection_name':
                    defaultOptionText = 'Choose Asset Name...';
                    break;
                default:
                    defaultOptionText = 'Choose Option...';
            }
            populateSelect(nextSelectId, nextOptions, defaultOptionText);
        }
    } else if (level === 3) {
        // Handle 'collection_name' selection
        const values = getSelectedValues(level);
        const collectionArray = getNextOptions(level - 1); // data up to 'about'
        const collection = collectionArray[values['collection_name']]; // index in array

        // Determine date selection type
        if (collection.collection_date === 'daily') {
            const dayElem = document.getElementById('day');
            dayElem.max = collection.end_date;
            dayElem.min = collection.start_date;
            dayElem.style.display = 'inline-block';
            dayElem.style.borderTop = '2px solid #37517e';
        } else if (collection.collection_date === 'monthly') {
            const monthElem = document.getElementById('month');
            monthElem.max = collection.end_date.slice(0, 7); // YYYY-MM
            monthElem.min = collection.start_date.slice(0, 7);
            monthElem.style.display = 'inline-block';
            monthElem.style.borderTop = '2px solid #37517e';
        } else {
            const yearElem = document.getElementById('year');
            yearElem.innerHTML = `<option selected disabled>Choose year...</option>`;
            for (let i = parseInt(collection.start_date); i <= parseInt(collection.end_date); i++) {
                yearElem.innerHTML += `<option value="${i}">${i}</option>`;
            }
            yearElem.style.display = 'inline-block';
            yearElem.style.borderTop = '2px solid #37517e';
        }
    } else {
        // Handle date selection and fetch data
        selectElem.style.borderTop = '2px solid green';
        let gas = document.getElementById('gas').value;
        const values = getSelectedValues(level);
        const collectionArray = getNextOptions(2); // data up to 'about'
        const collection = collectionArray[values['collection_name']];
        let dateValue = values[selectedIds[level]];
        if (selectedIds[level] === 'month' || selectedIds[level] === 'day') {
            dateValue = dateValue.split('-').join('');
        }
        colorValue = collection.color;
        document.getElementById('show-stats').onclick = function() {
            window.location.href = `stats.html#${collection.collection_name}&${collection.asset_name}&${gas}`;
        };
        fetchAndUpdateMap(collection, dateValue, colorValue);
    }
}

// Function to fetch and update the map
function fetchAndUpdateMap(collection, dateValue, colorValue) {
    document.querySelector('.overlay-map').style.display = 'block';
    fetch(`https://www.amartil.com/mypythonapp/GetItem/${collection.collection_name}/${collection.asset_name}/${dateValue}/${colorValue}`)
    //fetch(`https://www.amartil.com/mypythonapp/Get_statistics/${collection.collection_name}/${collection.asset_name}`)
        .then(response => response.text())
        .then(data => {
            data += `<style>
                        body { margin: 0; height: 100%;}
                        </style>`;
            document.getElementById('map-viewer').srcdoc = data;
            document.getElementById('show-stats').style.display = 'inline-block';
            document.querySelector('.overlay-map').style.display = 'none';
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            document.querySelector('.overlay-map').style.display = 'none';
        });
}

// Initialize
(async function init() {
    try {
        const response = await fetch('index.json');
        jsonData = await response.json();
        populateSelect('type', jsonData, 'Choose Source...');
    } catch (error) {
        console.error('Error fetching data:', error);
    }

    // Attach event listeners
    for (let i = 0; i < selectedIds.length; i++) {
        const selectId = selectedIds[i];
        const selectElem = document.getElementById(selectId);
        if (selectElem) {
            selectElem.addEventListener('change', function () {
                onSelectChange(i);
            });
        }
    }
    getUrlHashParam();
})();
