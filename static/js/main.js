function water(bookmark_id, csrf_token, is_nearest_page) {
    $.ajax({
        url: "water/" + bookmark_id,
        type: "POST",
        data: {
            'csrfmiddlewaretoken': csrf_token,
        },
        success: function (json) {
            if (is_nearest_page === "true") {
                document.getElementById("last_watering_" + bookmark_id).textContent = json["last_watering_for_nearest"]
            }
            else {
                document.getElementById("last_watering").textContent = json["last_watering"]
            }
        },
        error: function (xhr, errmsg, err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
}

function star(note_id, csrf_token) {
    $.ajax({
        url: "star/" + note_id,
        type: "POST",
        data: {
            'csrfmiddlewaretoken': csrf_token,
        },
        success: function (html) {
            document.getElementById("note-block").innerHTML = html.toString();
        },
        error: function (xhr, errmsg, err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
}

function delete_bookmark(bookmark_id, csrf_token) {
    $.ajax({
        url: "delete_bookmark/" + bookmark_id,
        type: "POST",
        data: {
            'csrfmiddlewaretoken': csrf_token,
        },
        success: function (html) {
            document.getElementById("note-block").innerHTML = html.toString();
        },
        error: function (xhr, errmsg, err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
}

function fertilize(bookmark_id, csrf_token, is_nearest_page) {
    $.ajax({
        url: "fertilize/" + bookmark_id,
        type: "POST",
        data: {
            'csrfmiddlewaretoken': csrf_token,
        },
        success: function (json) {
            if (is_nearest_page === "true") {
                document.getElementById("last_fertilize_" + bookmark_id).textContent = json["last_fertilize_for_nearest"]
            }
            else {
                document.getElementById("last_fertilize").textContent = json["last_fertilize"]
            }
        },
        error: function (xhr, errmsg, err) {
            console.log(xhr.status + ": " + xhr.responseText);
        }
    });
}