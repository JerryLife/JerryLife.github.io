// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-home",
    title: "Home",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-publications",
          title: "Publications",
          description: "Selected work and a complete publication record.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/publications/";
          },
        },{id: "nav-group",
          title: "Group",
          description: "I have been fortunate to work with many wonderful students and look forward to meeting more.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/supervision/";
          },
        },{id: "nav-service",
          title: "Service",
          description: "Professional services in academic communities",
          section: "Navigation",
          handler: () => {
            window.location.href = "/service/";
          },
        },{id: "nav-cv",
          title: "CV",
          description: "Curriculum Vitae",
          section: "Navigation",
          handler: () => {
            window.location.href = "/cv/";
          },
        },{id: "books-the-godfather",
          title: 'The Godfather',
          description: "",
          section: "Books",handler: () => {
              window.location.href = "/books/the_godfather/";
            },},{id: "news-i-received-the-dean-s-graduate-research-excellence-award-from-the-nus-school-of-computing-for-2022-2023",
          title: 'I received the Dean’s Graduate Research Excellence Award from the NUS School of...',
          description: "",
          section: "News",},{id: "news-one-paper-accepted-to-iclr-2024-zhaomin-wu-junyi-hou-bingsheng-he-vertibench-advancing-feature-distribution-diversity-in-vertical-federated-learning-benchmarks",
          title: 'One paper accepted to ICLR 2024. Zhaomin Wu, Junyi Hou, Bingsheng He. VertiBench:...',
          description: "",
          section: "News",},{id: "news-i-passed-my-ph-d-defense",
          title: 'I passed my Ph.D. defense.',
          description: "",
          section: "News",},{id: "news-our-paper-deltaboost-gradient-boosted-trees-with-efficient-machine-unlearning-received-the-honorable-mention-for-best-artifact-at-sigmod-2023",
          title: 'Our paper “DeltaBoost: Gradient Boosted Trees with Efficient Machine Unlearning” received the Honorable...',
          description: "",
          section: "News",},{id: "news-i-received-an-honorable-mention-for-the-best-ph-d-thesis-award-from-the-nus-school-of-computing",
          title: 'I received an Honorable Mention for the Best Ph.D. Thesis Award from the...',
          description: "",
          section: "News",},{id: "news-one-paper-accepted-to-neurips-2024-zhaomin-wu-junyi-hou-yiqun-diao-and-bingsheng-he-federated-transformer-multi-party-vertical-federated-learning-on-practical-fuzzily-linked-data",
          title: 'One paper accepted to NeurIPS 2024. Zhaomin Wu, Junyi Hou, Yiqun Diao, and...',
          description: "",
          section: "News",},{id: "news-i-received-the-best-research-staff-award-from-the-nus-institute-of-data-science",
          title: 'I received the Best Research Staff Award from the NUS Institute of Data...',
          description: "",
          section: "News",},{id: "news-invited-talk-bridging-private-data-silo-with-machine-learning-at-nus-open-house-2025",
          title: 'Invited talk: “Bridging Private Data Silo with Machine Learning” at NUS Open House...',
          description: "",
          section: "News",},{id: "news-one-paper-accepted-to-acl-2025-zhen-qin-zhaomin-wu-bingsheng-he-shuiguang-deng-federated-data-efficient-instruction-tuning-for-large-language-models",
          title: 'One paper accepted to ACL 2025. Zhen Qin, Zhaomin Wu, Bingsheng He, Shuiguang...',
          description: "",
          section: "News",},{id: "news-invited-talk-towards-practical-vertical-federated-learning-systems-at-dasfaa-2025-trust-day-on-behalf-of-prof-bingsheng-he",
          title: 'Invited talk: “Towards Practical Vertical Federated Learning Systems” at DASFAA 2025 Trust Day,...',
          description: "",
          section: "News",},{id: "news-one-paper-accepted-to-emnlp-2025-zhaomin-wu-jizhou-guo-junyi-hou-bingsheng-he-lixin-fan-qiang-yang-model-based-large-language-model-customization-as-service",
          title: 'One paper accepted to EMNLP 2025. Zhaomin Wu*, Jizhou Guo*, Junyi Hou, Bingsheng...',
          description: "",
          section: "News",},{id: "news-one-paper-accepted-to-kdd-2026-jizhou-guo-zhaomin-wu-hanchen-yang-philip-s-yu-mining-intrinsic-rewards-from-llm-hidden-states-for-efficient-best-of-n-sampling",
          title: 'One paper accepted to KDD 2026. Jizhou Guo, Zhaomin Wu, Hanchen Yang, Philip...',
          description: "",
          section: "News",},{id: "news-one-paper-accepted-to-www-2026-oral-yicheng-zhang-zhen-qin-zhaomin-wu-jian-hou-shuiguang-deng-personalized-federated-fine-tuning-for-llms-via-data-driven-heterogeneous-model-architectures",
          title: 'One paper accepted to WWW 2026 (Oral). Yicheng Zhang, Zhen Qin, Zhaomin Wu,...',
          description: "",
          section: "News",},{id: "news-keynote-bridging-data-silos-with-practical-federated-learning-at-the-aaai-2026-flca-workshop",
          title: 'Keynote: “Bridging Data Silos with Practical Federated Learning” at the AAAI 2026 FLCA...',
          description: "",
          section: "News",},{id: "news-two-papers-accepted-to-iclr-2026-for-oral-presentation-1-oral-zhaomin-wu-haodong-zhao-ziyang-wang-jizhou-guo-qian-wang-bingsheng-he-llm-dna-tracing-model-evolution-via-functional-representations-oral-zhaomin-wu-mingzhe-du-ng-see-kiong-bingsheng-he-beyond-prompt-induced-lies-investigating-llm-deception-on-benign-prompts",
          title: 'Two papers accepted to ICLR 2026 for Oral Presentation (1%). [Oral] Zhaomin Wu,...',
          description: "",
          section: "News",},{id: "news-one-paper-accepted-to-icde-2026-zhaomin-wu-ziyang-wang-bingsheng-he-wikidbgraph-a-data-management-benchmark-suite-for-collaborative-learning-over-database-silos",
          title: 'One paper accepted to ICDE 2026. Zhaomin Wu*, Ziyang Wang*, Bingsheng He. WikiDBGraph:...',
          description: "",
          section: "News",},{id: "news-i-received-the-nrf-postdoctoral-award-to-support-my-research-on-ai-powered-psychological-counselling-systems",
          title: 'I received the NRF Postdoctoral Award to support my research on AI-powered psychological...',
          description: "",
          section: "News",},{id: "news-i-received-the-google-cloud-research-credit-award-to-support-my-research",
          title: 'I received the Google Cloud Research Credit Award to support my research.',
          description: "",
          section: "News",},{id: "news-invited-talk-when-data-and-models-stay-hidden-toward-trustworthy-ai-collaboration-at-université-de-montréal-udem-and-mila",
          title: 'Invited talk: “When Data and Models Stay Hidden: Toward Trustworthy AI Collaboration” at...',
          description: "",
          section: "News",},{id: "news-i-received-the-icml-2026-gold-reviewer-award-top-25-of-reviewers",
          title: 'I received the ICML 2026 Gold Reviewer Award (top 25% of reviewers).',
          description: "",
          section: "News",},{id: "news-invited-talk-managing-data-and-model-silos-for-real-world-ai-systems-at-hong-kong-baptist-university",
          title: 'Invited talk: “Managing Data and Model Silos for Real-World AI Systems” at Hong...',
          description: "",
          section: "News",},{id: "news-two-papers-accepted-to-emnlp-2026-findings-haodong-zhao-jidong-li-zhaomin-wu-tianjie-ju-zhuosheng-zhang-bingsheng-he-gongshen-liu-reasoning-or-rambling-exploring-the-effect-of-thinking-on-agent-persuasion-qian-wang-zhongyi-tong-nuo-chen-zhaomin-wu-bingsheng-he-crossalpha-an-annual-report-benchmark-for-cross-market-factor-research",
          title: 'Two papers accepted to EMNLP 2026 Findings. Haodong Zhao, Jidong Li, Zhaomin Wu†,...',
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
        id: 'social-email',
        title: 'email',
        section: 'Socials',
        handler: () => {
          window.open("mailto:%7A%68%61%6F%6D%69%6E@%68%6B%62%75.%65%64%75.%68%6B", "_blank");
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
