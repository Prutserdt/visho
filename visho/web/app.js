/* global L, locations */

const application = document.getElementById("application");
const splitter = document.getElementById("splitter");
const listElement = document.getElementById("pictures");
const sentinel = document.getElementById("list-sentinel");

const map = L.map("map").setView([37.5, 14], 8);

/*
 * Esri ArcGIS World Street Map.
 * This does not require a CARTO API key.
 */
L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/"
    + "World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    {
        maxZoom: 19,
        attribution:
            "Tiles &copy; Esri — Source: Esri, "
            + "DeLorme, NAVTEQ, USGS, Intermap, "
            + "iPC, NRCAN, Esri Japan, METI, Esri China "
            + "(Hong Kong), Esri Korea, Esri (Thailand), "
            + "TomTom, MapmyIndia, &copy; OpenStreetMap contributors"
    }
).addTo(map);

const markers = [];
const rows = new Map();
let currentPictureIndex = -1;
let filteredIndices = locations.map((_, index) => index);
let renderedCount = 0;
let imageZoom = 1;
let imageOffsetX = 0;
let imageOffsetY = 0;
let slideshowTimer = null;

/* ---------- Map markers ---------- */

function markerStyle(selected) {
    return selected
        ? {radius: 11, color: "#8b0000", weight: 3, fillColor: "#ff0000", fillOpacity: 1}
        : {radius: 7, color: "#0645ad", weight: 2, fillColor: "#3388ff", fillOpacity: .95};
}

locations.forEach(function(location, index) {
    if (!location.has_gps) {
        return;
    }
    const marker = L.circleMarker(
        [location.latitude, location.longitude],
        markerStyle(false)
    ).addTo(map);
    marker.pictureIndex = index;
    marker.bindTooltip(location.name);
    marker.on("click", function() {
        showPicture(index, false);
    });
    markers.push(marker);
});

function updateMarkerStyles() {
    markers.forEach(function(marker) {
        marker.setStyle(markerStyle(marker.pictureIndex === currentPictureIndex));
    });
}

function zoomToLocations(indices) {
    const gps = indices
        .map(index => locations[index])
        .filter(location => location.has_gps);
    if (!gps.length) {
        alert("No selected pictures have GPS data.");
        return;
    }
    if (gps.length === 1) {
        map.setView([gps[0].latitude, gps[0].longitude], 14);
        return;
    }
    map.fitBounds(
        L.latLngBounds(gps.map(location => [location.latitude, location.longitude])),
        {padding: [30, 30]}
    );
}

function zoomToAllPictures() {
    zoomToLocations(locations.map((_, index) => index));
}

function zoomToSelectedPicture() {
    if (currentPictureIndex < 0) {
        alert("No picture is currently selected.");
        return;
    }
    zoomToLocations([currentPictureIndex]);
}

function updateGoogleMapsButton() {
    const button = document.getElementById("google-maps-button");
    const location = locations[currentPictureIndex];
    button.disabled = !location || !location.has_gps;
}

function openSelectedLocationInGoogleMaps() {
    const location = locations[currentPictureIndex];
    if (!location || !location.has_gps) {
        alert("The selected picture has no GPS data.");
        return;
    }
    const url =
        "https://www.google.com/maps/search/?api=1&query="
        + encodeURIComponent(location.latitude + "," + location.longitude);
    window.open(url, "_blank", "noopener");
}

/* ---------- Image viewer zoom ---------- */

function updateImageTransform() {
    document.getElementById("viewer-image").style.transform =
        "translate(" + imageOffsetX + "px, " + imageOffsetY + "px) scale(" + imageZoom + ")";
    document.getElementById("zoom-level").textContent =
        Math.round(imageZoom * 100) + "%";
}

function resetImageZoom() {
    imageZoom = 1;
    imageOffsetX = 0;
    imageOffsetY = 0;
    updateImageTransform();
}

function zoomImageIn() {
    imageZoom = Math.min(imageZoom + .25, 5);
    updateImageTransform();
}

function zoomImageOut() {
    imageZoom = Math.max(imageZoom - .25, 1);
    if (imageZoom === 1) {
        imageOffsetX = 0;
        imageOffsetY = 0;
    }
    updateImageTransform();
}

/* ---------- Picture list ---------- */

function updateListStatus() {
    const number = currentPictureIndex < 0 ? renderedCount : currentPictureIndex + 1;
    document.getElementById("list-status").textContent =
        "Showing " + number + " of " + locations.length + " pictures";
}

function createPictureRow(index) {
    const location = locations[index];
    const row = document.createElement("div");
    row.className = "picture-row";

    const thumbnail = document.createElement("img");
    thumbnail.className = "picture-thumbnail";
    thumbnail.alt = location.name;
    thumbnail.loading = "lazy";
    thumbnail.src = location.thumbnail;

    const text = document.createElement("span");
    const name = document.createElement("div");
    name.className = "picture-name";
    name.textContent = location.name;
    text.appendChild(name);

    if (!location.has_gps) {
        const gps = document.createElement("div");
        gps.className = "no-gps";
        gps.textContent = "No GPS data";
        text.appendChild(gps);
    }

    row.appendChild(thumbnail);
    row.appendChild(text);
    row.addEventListener("click", function() {
        showPicture(index, false);
    });
    rows.set(index, row);
    return row;
}

function renderNextBatch() {
    const nextCount = Math.min(renderedCount + 100, filteredIndices.length);
    const fragment = document.createDocumentFragment();
    for (let position = renderedCount; position < nextCount; position++) {
        fragment.appendChild(createPictureRow(filteredIndices[position]));
    }
    listElement.appendChild(fragment);
    renderedCount = nextCount;
    updateListStatus();
}

function updateCurrentRow() {
    rows.forEach(function(row, index) {
        row.classList.toggle("current", index === currentPictureIndex);
    });
}

function ensureRowIsRendered(index) {
    const position = filteredIndices.indexOf(index);
    while (renderedCount <= position && renderedCount < filteredIndices.length) {
        renderNextBatch();
    }
    const row = rows.get(index);
    if (row) {
        row.scrollIntoView({behavior: "smooth", block: "center"});
    }
}

/* ---------- Navigation ---------- */

function showPicture(index, zoomMap) {
    if (!locations.length) {
        return;
    }
    currentPictureIndex = index;
    const location = locations[index];
    document.getElementById("viewer-title").textContent = location.name;

    const image = document.getElementById("viewer-image");
    image.src = location.picture;
    image.alt = location.name;

    resetImageZoom();
    ensureRowIsRendered(index);
    updateCurrentRow();
    updateMarkerStyles();
    updateGoogleMapsButton();
    updateListStatus();

    if (zoomMap && location.has_gps) {
        map.setView([location.latitude, location.longitude], 14);
    }
}

function showPreviousPicture() {
    if (!locations.length) {
        return;
    }
    showPicture((currentPictureIndex - 1 + locations.length) % locations.length, false);
}

function showNextPicture() {
    if (!locations.length) {
        return;
    }
    showPicture((currentPictureIndex + 1) % locations.length, false);
}

/* ---------- Slideshow ---------- */

function getSlideshowInterval() {
    const input = document.getElementById("slideshow-interval");
    const seconds = Number(input.value);

    if (!Number.isFinite(seconds) || seconds < 1) {
        input.value = 5;
        return 5;
    }

    return seconds;
}


function updateSlideshowButton() {
    const startButton = document.getElementById("slideshow-button");
    const stopButton = document.getElementById("slideshow-stop-button");
    const running = slideshowTimer !== null;

    startButton.disabled = running;
    startButton.setAttribute("aria-pressed", running ? "true" : "false");
    stopButton.disabled = !running;
}


function stopSlideshow() {
    if (slideshowTimer !== null) {
        clearInterval(slideshowTimer);
        slideshowTimer = null;
    }
    updateSlideshowButton();
}

function startSlideshow() {
    if (!locations.length) {
        return;
    }

    stopSlideshow();
    const interval = getSlideshowInterval() * 1000;
    slideshowTimer = setInterval(showNextPicture, interval);
    updateSlideshowButton();
}


document.getElementById("slideshow-interval").addEventListener("change", function() {
    const seconds = Number(this.value);
    if (!Number.isFinite(seconds) || seconds < 1) {
        this.value = 5;
    }
    if (slideshowTimer !== null) {
        startSlideshow();
    }
});

updateSlideshowButton();

/* ---------- Resizable map/viewer divider ---------- */

let resizing = false;

splitter.addEventListener("pointerdown", function(event) {
    resizing = true;
    splitter.classList.add("dragging");
    splitter.setPointerCapture(event.pointerId);
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
});

splitter.addEventListener("pointermove", function(event) {
    if (!resizing) {
        return;
    }
    const rect = application.getBoundingClientRect();
    const listWidth = document.getElementById("picture-list").getBoundingClientRect().width;
    const splitterWidth = 8;
    const minimumMapWidth = 220;
    const minimumViewerWidth = 220;
    const mapStart = rect.left + listWidth;
    const totalWidth = rect.width - listWidth - splitterWidth;

    let mapWidth = event.clientX - mapStart;
    mapWidth = Math.max(mapWidth, minimumMapWidth);
    mapWidth = Math.min(mapWidth, totalWidth - minimumViewerWidth);

    application.style.gridTemplateColumns =
        listWidth + "px " + mapWidth + "px " + splitterWidth + "px "
        + "minmax(" + minimumViewerWidth + "px, 1fr)";
    map.invalidateSize();
});

function stopResizing(event) {
    resizing = false;
    splitter.classList.remove("dragging");
    document.body.style.cursor = "";
    document.body.style.userSelect = "";
    if (event && splitter.hasPointerCapture(event.pointerId)) {
        splitter.releasePointerCapture(event.pointerId);
    }
    map.invalidateSize();
}

splitter.addEventListener("pointerup", stopResizing);
splitter.addEventListener("pointercancel", stopResizing);

/* ---------- Image zooming and dragging ---------- */

const imageContainer = document.getElementById("viewer-image-container");

imageContainer.addEventListener("wheel", function(event) {
    event.preventDefault();
    if (event.deltaY < 0) {
        zoomImageIn();
    } else {
        zoomImageOut();
    }
}, {passive: false});

let draggingImage = false;
let dragStartX = 0;
let dragStartY = 0;

imageContainer.addEventListener("pointerdown", function(event) {
    if (imageZoom <= 1) {
        return;
    }
    draggingImage = true;
    dragStartX = event.clientX - imageOffsetX;
    dragStartY = event.clientY - imageOffsetY;
    imageContainer.classList.add("dragging");
    imageContainer.setPointerCapture(event.pointerId);
});

imageContainer.addEventListener("pointermove", function(event) {
    if (!draggingImage) {
        return;
    }
    imageOffsetX = event.clientX - dragStartX;
    imageOffsetY = event.clientY - dragStartY;
    updateImageTransform();
});

imageContainer.addEventListener("pointerup", function(event) {
    draggingImage = false;
    imageContainer.classList.remove("dragging");
    if (imageContainer.hasPointerCapture(event.pointerId)) {
        imageContainer.releasePointerCapture(event.pointerId);
    }
});

imageContainer.addEventListener("pointercancel", function() {
    draggingImage = false;
    imageContainer.classList.remove("dragging");
});

/* ---------- Keyboard shortcuts ---------- */

document.addEventListener("keydown", function(event) {
    if (event.key === "p") {
        showPreviousPicture();
    } else if (event.key === "n") {
        showNextPicture();
    } else if (event.key === "+" || event.key === "=") {
        zoomImageIn();
    } else if (event.key === "-") {
        zoomImageOut();
    } else if (event.key === "0") {
        resetImageZoom();
    }
});

/* ---------- Lazy list rendering + start-up ---------- */

const listObserver = new IntersectionObserver(
    function(entries) {
        if (entries[0].isIntersecting && renderedCount < filteredIndices.length) {
            renderNextBatch();
        }
    },
    {root: document.getElementById("picture-list"), rootMargin: "500px"}
);
listObserver.observe(sentinel);

renderNextBatch();

if (locations.length > 0) {
    showPicture(0, false);
    zoomToAllPictures();
} else {
    updateGoogleMapsButton();
}
