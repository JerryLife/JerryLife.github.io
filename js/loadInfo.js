import info from '../assets/json/info.json' assert {type: 'json'};

function load_info() {
    // basic info
    document.getElementById("first-name").innerHTML = info.first_name;
    document.getElementById("last-name").innerHTML = info.last_name;
    document.getElementById("email").innerHTML = info.email;
    document.getElementById("email").href = "mailto:" + info.email;
    document.getElementById("address").innerHTML = info.address;
    // document.getElementById("phone").innerHTML = info.phone;
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


function load_award() {
    const award_list = document.getElementById("award-list");
    info.award.forEach((item) => {
        // award icon and container
        const li = document.createElement("li");
        const award_icon = document.createElement("span");
        award_icon.className = "fa-li";
        const award_icon_i = document.createElement("i");
        award_icon_i.className = "fas fa-trophy text-warning";
        award_icon.appendChild(award_icon_i);
        li.appendChild(award_icon);

        // award content
        const award_content = document.createElement("div");
        award_content.className = "mt-3 fs-6 fw-bold";
        if (item.event != null) {
            award_content.innerHTML = `${item.title} - ${item.event}) - ${item.organization}, ${item.year}`;
        } else {
            award_content.innerHTML = `${item.title} - ${item.organization}, ${item.year}`;
        }
        li.appendChild(award_content);

        const award_comment = document.createElement("div");
        if (item.description != null) {
            award_comment.innerHTML = item.description;
            award_comment.className = "mb-3 fs-light";
            li.appendChild(award_comment);
        }

        award_list.appendChild(li);
    });
}


function load_skill() {
    // programming language
    const programming_language = document.getElementById("programming-language");

    const familiar_pl_li = document.createElement("li");
    familiar_pl_li.innerHTML = "<span class=\"fa-li\"><i class=\"fas fa-check\"></i></span>";
    familiar_pl_li.innerHTML += "<b>Familiar: </b>";
    familiar_pl_li.innerHTML += info.skill.programming_language.familiar.join(", ");
    programming_language.appendChild(familiar_pl_li);

    const used_pl_li = document.createElement("li");
    used_pl_li.innerHTML = "<span class=\"fa-li\"><i class=\"fas fa-check\"></i></span>";
    used_pl_li.innerHTML += "<b>Used: </b>";
    used_pl_li.innerHTML += info.skill.programming_language.used.join(", ");
    programming_language.appendChild(used_pl_li);

    // tool
    const tool = document.getElementById("tool");

    const familiar_tool_li = document.createElement("li");
    familiar_tool_li.innerHTML = "<span class=\"fa-li\"><i class=\"fas fa-check\"></i></span>";
    familiar_tool_li.innerHTML += "<b>Familiar: </b>";
    familiar_tool_li.innerHTML += info.skill.tool.familiar.join(", ");
    tool.appendChild(familiar_tool_li);

    const used_tool_li = document.createElement("li");
    used_tool_li.innerHTML = "<span class=\"fa-li\"><i class=\"fas fa-check\"></i></span>";
    used_tool_li.innerHTML += "<b>Used: </b>";
    used_tool_li.innerHTML += info.skill.tool.used.join(", ");
    tool.appendChild(used_tool_li);

    // communicating language
    const communicating_language = document.getElementById("communicating-language");
    const familiar_cl_li = document.createElement("li");
    familiar_cl_li.innerHTML = "<span class=\"fa-li\"><i class=\"fas fa-check\"></i></span>";
    familiar_cl_li.innerHTML += info.skill.language.join(", ");
    communicating_language.appendChild(familiar_cl_li);

}

function load_service() {
    // conference
    const conference_list = document.getElementById("conference-reviewer");
    info.service.conference.forEach((item) => {
        const conference_li = document.createElement("li");
        conference_li.innerHTML += item;
        conference_list.appendChild(conference_li);
    });

    // journal
    const journal_list = document.getElementById("journal-reviewer");
    info.service.journal.forEach((item) => {
        const journal_li = document.createElement("li");
        journal_li.innerHTML += item;
        journal_list.appendChild(journal_li);
    });

    // tutorial
    const tutorial_list = document.getElementById("tutorial");
    info.service.tutorial.forEach((item) => {
        const tutorial_li = document.createElement("li");
        tutorial_li.innerHTML += item;
        tutorial_list.appendChild(tutorial_li);
    });
}

function load_all() {
    load_info();
    load_education();
    load_publication();
    load_award();
    load_skill();
    load_service();
}

load_all();