%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Medium Length Professional CV - RESUME CLASS FILE
%
% Based on the LaTeXTemplates resume class by Trey Hunner.
% Copying and distribution of this file, with or without modification,
% are permitted in any medium without royalty provided the copyright
% notice and this notice are preserved. This file is offered as-is,
% without any warranty.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\ProvidesClass{resume}[2010/07/10 v0.9 Resume class]

\LoadClass[11pt,letterpaper]{article}
\usepackage{mathpazo}
\usepackage[parfill]{parskip}
\usepackage{array}
\usepackage{ifthen}
\usepackage{textcase}

\pagestyle{empty}

%----------------------------------------------------------------------------------------
% Headings
%----------------------------------------------------------------------------------------

\def \name#1{\def\@name{#1}}
\def \@name {}

\def \addressSep {$\diamond$}

\let \@addressone \relax
\let \@addresstwo \relax
\let \@addressthree \relax

\def \address #1{
  \@ifundefined{@addresstwo}{
    \def \@addresstwo {#1}
  }{
  \@ifundefined{@addressthree}{
    \def \@addressthree {#1}
  }{
    \def \@addressone {#1}
  }}
}

\def \printaddress #1{
  \begingroup
    \def \\ {\addressSep\ }
    \centerline{#1}
  \endgroup
  \par
  \addressskip
}

\def \printname {
  \begingroup
    \hfil{\MakeUppercase{\namesize\bf \@name}}\hfil
    \nameskip\break
  \endgroup
}

\newcommand{\rSectionSupplementalTextFixedSize}{\footnotesize}

\let\ori@document=\document
\renewcommand{\document}{
  \ori@document
  \printname
  \@ifundefined{@addressone}{}{\printaddress{\@addressone}}
  \@ifundefined{@addresstwo}{}{\printaddress{\@addresstwo}}
  \@ifundefined{@addressthree}{}{\printaddress{\@addressthree}}
}

%----------------------------------------------------------------------------------------
% Sections
%----------------------------------------------------------------------------------------

\newenvironment{rSection}[1]{
  \sectionskip
  \nopagebreak[4]
  \MakeUppercase{\bf #1}
  \nopagebreak[4]
  \sectionlineskip
  \nopagebreak[4]
  \hrule
  \nopagebreak[4]
  \begin{list}{}{
    \setlength{\leftmargin}{0.6em}
  }
  \item[]
}{
  \end{list}
}

\newenvironment{rSectionTiny}[2]{
  \sectionskip
  \nopagebreak[4]
  \noindent
  \MakeUppercase{\bf #1}
  \nopagebreak[4]
  \hspace{0.1em}
  \noindent {\rSectionSupplementalTextFixedSize #2}
  \nopagebreak[4]
  \sectionlineskip
  \nopagebreak[4]
  \hrule
  \nopagebreak[4]
  \begin{list}{}{
    \setlength{\leftmargin}{0.6em}
  }
  \item[]
}{
  \end{list}
}

\newenvironment{rSubsection}[4]{
  {\bf #1} \hfill {#2}
  \ifthenelse{\equal{#3}{}}{}{
  \\
  {\em #3} \hfill {\em #4}
  }\smallskip
  \begin{list}{$\cdot$}{\leftmargin=0em}
    \itemsep -0.5em \vspace{-0.5em}
  }{
  \end{list}
  \vspace{0.5em}
}

\def\namesize{\huge}
\def\addressskip{\smallskip}
\def\sectionlineskip{\medskip}
\def\nameskip{\bigskip}
\def\sectionskip{\medskip}
