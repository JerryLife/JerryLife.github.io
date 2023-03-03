import info from '../assets/json/info.json' assert {type: 'json'};

function load_info() {
    // basic info
    document.getElementById("first-name").innerHTML = info.first_name;
    document.getElementById("last-name").innerHTML = info.last_name;
    document.getElementById("email").innerHTML = info.email;
    document.getElementById("email").href = "mailto:" + info.email;
    document.getElementById("address").innerHTML = info.address;
    document.getElementById("phone").innerHTML = info.phone;
    document.getElementById("about-me").innerHTML = info.about_me;

    document.getElementById("linkedin").href = info.linkedin;
    document.getElementById("github").href = info.github;
    document.getElementById("google-scholar").href = info.google_scholar;
}

function load_education() {
    // education
    const education_list = document.getElementById("edu_list");
    info.education.forEach((item) => {
        const div = document.createElement("div");
        div.className = "resume-item d-flex flex-column flex-md-row justify-content-between mb-5";
        // left: school information
        const subdiv_content = document.createElement("div");
        subdiv_content.className = "flex-grow-1";
        const subdiv_content_h3 = document.createElement("h3");
        subdiv_content_h3.className = "mb-0";
        subdiv_content_h3.innerHTML = item.school;      // school name
        subdiv_content.appendChild(subdiv_content_h3);
        const subdiv_content_div = document.createElement("div");
        subdiv_content_div.className = "subheading mb-3";
        subdiv_content_div.innerHTML = item.degree;
        subdiv_content.appendChild(subdiv_content_div);
        if (item.major != null) {
            const subdiv_content_div1 = document.createElement("div");
            subdiv_content_div1.innerHTML = item.major;
            subdiv_content.appendChild(subdiv_content_div1);
        }
        if (item.description != null) {
            const subdiv_content_p = document.createElement("p");
            subdiv_content_p.innerHTML = item.description;
            subdiv_content.appendChild(subdiv_content_p);
        } else {
            // append a blank line
            const subdiv_content_p = document.createElement("p");
            subdiv_content_p.innerHTML = "";
            subdiv_content.appendChild(subdiv_content_p);
        }


        // right: duration
        const subdiv_date = document.createElement("div");
        subdiv_date.className = "flex-shrink-0";
        const span = document.createElement("span");
        span.className = "text-primary";
        span.innerHTML = item.start_date + " - " + item.end_date;
        subdiv_date.appendChild(span);

        // append to div
        div.appendChild(subdiv_content);
        div.appendChild(subdiv_date);
        education_list.appendChild(div);
    });
}


function load_publication() {
    // publication
    const publication_list = document.getElementById("pub_list");

    // sort the publication by year
    info.publication.sort((a, b) => (a.year > b.year) ? -1 : 1);

    info.publication.forEach((item) => {
        // read title
        const div = document.createElement("div");
        div.className = "resume-item mb-5";

        const title = document.createElement("div");
        title.className = "mb-0 fs-5";
        const title_text = `<b>${item.title}</b>`;
        if (item.pub_link != null) {
            title.innerHTML = `<a href="${item.pub_link}">${title_text}</a>`;
        } else {
            title.innerHTML = title_text;
        }
        if (item.pdf_link != null) {
            title.innerHTML += ` (<a href="${item.pdf_link}">pdf</a>)`;
        }
        if (item.code_link != null) {
            title.innerHTML += ` (<a href="${item.code_link}">code</a>)`;
        }

        // read authors (bold me)
        const authors = document.createElement("div");
        authors.className = "mb-0";
        const full_name = info.first_name + " " + info.last_name;
        const regExIgnoreCase = new RegExp(full_name, "ig");
        authors.innerHTML = item.authors.replace(regExIgnoreCase, `<b>${full_name}</b>`);

        // read publication with abbreviation (bold abbreviation)
        const publication = document.createElement("div");
        publication.className = "mb-0";
        publication.innerHTML = `${item.publication} (<b>${item.pub_abbr}</b>)`;

        // append to div
        div.appendChild(title);
        div.appendChild(authors);
        div.appendChild(publication);
        publication_list.appendChild(div);
    });
}


function load_all() {
    load_info();
    load_education();
    load_publication();
}

load_all();