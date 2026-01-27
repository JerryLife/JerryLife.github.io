// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-about",
    title: "About",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-publications",
          title: "Publications",
          description: "Publications and Preprints.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/publications/";
          },
        },{id: "nav-service",
          title: "Service",
          description: "Professional services in academic communities",
          section: "Navigation",
          handler: () => {
            window.location.href = "/service/";
          },
        },{id: "nav-teaching",
          title: "Teaching",
          description: "Teaching experience and mentorship",
          section: "Navigation",
          handler: () => {
            window.location.href = "/teaching/";
          },
        },{id: "nav-cv",
          title: "CV",
          description: "Cirriculum Vitae",
          section: "Navigation",
          handler: () => {
            window.location.href = "/cv/";
          },
        },{id: "nav-repositories",
          title: "Repositories",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/repositories/";
          },
        },{id: "books-the-godfather",
          title: 'The Godfather',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the_godfather/";
            },},{id: "news-i-have-received-the-dean-s-graduate-research-excellence-award-from-school-of-computing-nus-for-academic-year-2022-2023",
          title: 'I have received the Dean’s Graduate Research Excellence Award from School of Computing,...',
          description: "",
          section: "News",},{id: "news-one-paper-accepted-in-iclr-2024-zhaomin-wu-junyi-hou-bingsheng-he-vertibench-advancing-feature-distribution-diversity-in-vertical-federated-learning-benchmarks",
          title: 'One paper accepted in ICLR 2024. Zhaomin Wu, Junyi Hou, Bingsheng He. VertiBench:...',
          description: "",
          section: "News",},{id: "news-i-have-passed-my-ph-d-defense",
          title: 'I have passed my Ph.D. defense! 🎉',
          description: "",
          section: "News",},{id: "news-our-paper-deltaboost-gradient-boosted-trees-with-efficient-machine-unlearning-by-zhaomin-wu-junhui-zhu-qinbin-li-bingsheng-he-has-been-awarded-the-honorable-mention-for-the-best-artifact-in-sigmod-2023",
          title: 'Our paper “DeltaBoost: Gradient Boosted Trees with Efficient Machine Unlearning” (by Zhaomin Wu,...',
          description: "",
          section: "News",},{id: "news-i-have-been-awarded-phd-thesis-award-honorable-mention-by-the-school-of-computing-soc-nus",
          title: 'I have been awarded PhD Thesis Award Honorable Mention by the School of...',
          description: "",
          section: "News",},{id: "news-one-paper-accepted-in-neurips-2024-zhaomin-wu-junyi-hou-yiqun-diao-and-bingsheng-he-federated-transformer-multi-party-vertical-federated-learning-on-practical-fuzzily-linked-data",
          title: 'One paper accepted in NeurIPS 2024. Zhaomin Wu, Junyi Hou, Yiqun Diao, and...',
          description: "",
          section: "News",},{id: "news-i-have-received-the-best-research-staff-award-from-institute-of-data-science-nus",
          title: 'I have received the Best Research Staff Award from Institute of Data Science,...',
          description: "",
          section: "News",},{id: "news-i-delivered-an-invited-talk-bridging-private-data-silo-with-machine-learning-at-the-nus-open-house-2025",
          title: 'I delivered an invited talk “Bridging Private Data Silo with Machine Learning” at...',
          description: "",
          section: "News",},{id: "news-one-paper-accepted-in-acl-2025-zhen-qin-zhaomin-wu-bingsheng-he-shuiguang-deng-federated-data-efficient-instruction-tuning-for-large-language-models",
          title: 'One paper accepted in ACL 2025. Zhen Qin, Zhaomin Wu, Bingsheng He, Shuiguang...',
          description: "",
          section: "News",},{id: "news-i-delivered-an-invited-talk-entitled-towards-practical-vertical-federated-learning-systems-on-behalf-of-prof-bingsheng-he-at-the-dasfaa-2025-trust-day",
          title: 'I delivered an invited talk entitled “Towards Practical Vertical Federated Learning Systems” on...',
          description: "",
          section: "News",},{id: "news-one-paper-accepted-in-emnlp-2025-zhaomin-wu-jizhou-guo-junyi-hou-bingsheng-he-lixin-fan-qiang-yang-model-based-large-language-model-customization-as-service",
          title: 'One paper accepted in EMNLP 2025. Zhaomin Wu*, Jizhou Guo*, Junyi Hou, Bingsheng...',
          description: "",
          section: "News",},{id: "news-one-paper-accepted-in-kdd-2026-jizhou-guo-zhaomin-wu-hanchen-yang-philip-s-yu-mining-intrinsic-rewards-from-llm-hidden-states-for-efficient-best-of-n-sampling",
          title: 'One paper accepted in KDD 2026. Jizhou Guo, Zhaomin Wu, Hanchen Yang, Philip...',
          description: "",
          section: "News",},{id: "news-one-paper-accepted-in-www-2026-yicheng-zhang-zhen-qin-zhaomin-wu-jian-hou-shuiguang-deng-personalized-federated-fine-tuning-for-llms-via-data-driven-heterogeneous-model-architectures",
          title: 'One paper accepted in WWW 2026. Yicheng Zhang, Zhen Qin, Zhaomin Wu, Jian...',
          description: "",
          section: "News",},{id: "news-two-papers-accepted-to-iclr-2026-zhaomin-wu-haodong-zhao-ziyang-wang-jizhou-guo-qian-wang-bingsheng-he-llm-dna-tracing-model-evolution-via-functional-representations-zhaomin-wu-mingzhe-du-ng-see-kiong-bingsheng-he-beyond-prompt-induced-lies-investigating-llm-deception-on-benign-prompts",
          title: 'Two papers accepted to ICLR 2026. Zhaomin Wu, Haodong Zhao, Ziyang Wang, Jizhou...',
          description: "",
          section: "News",},{id: "news-i-was-invited-to-give-a-keynote-entitled-bridging-data-silos-with-practical-federated-learning-at-the-aaai-2026-flca-workshop",
          title: 'I was invited to give a keynote entitled “Bridging Data Silos with Practical...',
          description: "",
          section: "News",},{id: "projects-project-1",
          title: 'project 1',
          description: "with background image",
          section: "Projects",handler: () => {
              window.location.href = "/projects/1_project/";
            },},{id: "projects-project-2",
          title: 'project 2',
          description: "a project with a background image and giscus comments",
          section: "Projects",handler: () => {
              window.location.href = "/projects/2_project/";
            },},{id: "projects-project-3-with-very-long-name",
          title: 'project 3 with very long name',
          description: "a project that redirects to another website",
          section: "Projects",handler: () => {
              window.location.href = "/projects/3_project/";
            },},{id: "projects-project-4",
          title: 'project 4',
          description: "another without an image",
          section: "Projects",handler: () => {
              window.location.href = "/projects/4_project/";
            },},{id: "projects-project-5",
          title: 'project 5',
          description: "a project with a background image",
          section: "Projects",handler: () => {
              window.location.href = "/projects/5_project/";
            },},{id: "projects-project-6",
          title: 'project 6',
          description: "a project with no image",
          section: "Projects",handler: () => {
              window.location.href = "/projects/6_project/";
            },},{id: "projects-project-7",
          title: 'project 7',
          description: "with background image",
          section: "Projects",handler: () => {
              window.location.href = "/projects/7_project/";
            },},{id: "projects-project-8",
          title: 'project 8',
          description: "an other project with a background image and giscus comments",
          section: "Projects",handler: () => {
              window.location.href = "/projects/8_project/";
            },},{id: "projects-project-9",
          title: 'project 9',
          description: "another project with an image 🎉",
          section: "Projects",handler: () => {
              window.location.href = "/projects/9_project/";
            },},{
        id: 'social-dblp',
        title: 'DBLP',
        section: 'Socials',
        handler: () => {
          window.open("https://dblp.org/pid/254/0918", "_blank");
        },
      },{
        id: 'social-email',
        title: 'email',
        section: 'Socials',
        handler: () => {
          window.open("mailto:%7A%68%61%6F%6D%69%6E@%6E%75%73.%65%64%75.%73%67", "_blank");
        },
      },{
        id: 'social-github',
        title: 'GitHub',
        section: 'Socials',
        handler: () => {
          window.open("https://github.com/JerryLife", "_blank");
        },
      },{
        id: 'social-linkedin',
        title: 'LinkedIn',
        section: 'Socials',
        handler: () => {
          window.open("https://www.linkedin.com/in/zhaomin-wu-958159258", "_blank");
        },
      },{
        id: 'social-orcid',
        title: 'ORCID',
        section: 'Socials',
        handler: () => {
          window.open("https://orcid.org/0000-0002-6463-0031", "_blank");
        },
      },{
        id: 'social-rss',
        title: 'RSS Feed',
        section: 'Socials',
        handler: () => {
          window.open("/feed.xml", "_blank");
        },
      },{
        id: 'social-scholar',
        title: 'Google Scholar',
        section: 'Socials',
        handler: () => {
          window.open("https://scholar.google.com/citations?user=QjehmgkAAAAJ", "_blank");
        },
      },{
      id: 'light-theme',
      title: 'Change theme to light',
      description: 'Change the theme of the site to Light',
      section: 'Theme',
      handler: () => {
        setThemeSetting("light");
      },
    },
    {
      id: 'dark-theme',
      title: 'Change theme to dark',
      description: 'Change the theme of the site to Dark',
      section: 'Theme',
      handler: () => {
        setThemeSetting("dark");
      },
    },
    {
      id: 'system-theme',
      title: 'Use system default theme',
      description: 'Change the theme of the site to System Default',
      section: 'Theme',
      handler: () => {
        setThemeSetting("system");
      },
    },];
