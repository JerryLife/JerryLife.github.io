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
\usepackage{xcolor}

\pagestyle{empty}

\newdimen\cvRemainingSpace
\newdimen\cvRequestedSpace
\newcommand{\cvNeedspace}[1]{%
  \par
  \begingroup
    \cvRemainingSpace=\pagegoal
    \advance\cvRemainingSpace by -\pagetotal
    \cvRequestedSpace=#1\relax
    \ifdim\cvRequestedSpace>\cvRemainingSpace
      \vfil\break
    \fi
  \endgroup
}

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
  \cvNeedspace{7\baselineskip}
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
  \cvNeedspace{7\baselineskip}
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

\newcommand{\cvSubheading}[1]{%
  \cvNeedspace{2\baselineskip}
  \noindent{\bf #1}\par\vspace{-0.2em}
  \nopagebreak[4]
}

\newcommand{\yearSeparator}[1]{%
  \cvNeedspace{4\baselineskip}
  \par\smallskip
  \noindent\begingroup
    \bfseries\textcolor{black!50}{#1}%
    \hspace{0.75em}%
    \textcolor{black!18}{\leaders\hrule height 0.3pt\hfill}%
  \endgroup
  \par\smallskip
}

\newcommand{\publicationYear}[1]{\yearSeparator{#1}}
\newcommand{\serviceYear}[1]{\yearSeparator{#1}}
\newcommand{\honorGroup}[1]{\yearSeparator{#1}}
\newcommand{\talkYear}[1]{\yearSeparator{#1}}
\newcommand{\teachingGroup}[1]{\yearSeparator{#1}}

\newcommand{\serviceLine}[2]{%
  \noindent\textbf{#1}: #2\par\vspace{-0.3em}%
}

\newcommand{\talkEntry}[4]{%
  \noindent
  \begin{tabular*}{\linewidth}{@{}p{0.78\linewidth}@{\extracolsep{\fill}}r@{}}
    \textbf{#1}: ``#2'' & #4
  \end{tabular*}\\
  #3\par\vspace{0.1em}%
}

\newcommand{\talkEntryWithUrl}[5]{%
  \noindent
  \begin{tabular*}{\linewidth}{@{}p{0.78\linewidth}@{\extracolsep{\fill}}r@{}}
    \textbf{#1}: ``\href{#5}{#2}'' & #4
  \end{tabular*}\\
  #3\par\vspace{0.1em}%
}

\newcommand{\honorEntry}[3]{%
  \noindent$\bullet$ \textbf{#1} \hfill #2\\
  #3\par\vspace{0.1em}%
}

\newcommand{\teachingEntry}[2]{%
  \noindent
  \begin{tabular*}{\linewidth}{@{}p{0.78\linewidth}@{\extracolsep{\fill}}r@{}}
    #1 & #2
  \end{tabular*}\par\vspace{-0.3em}%
}

\newcommand{\mentoredStudentEntry}[3]{%
  \noindent
  \begin{tabular*}{\linewidth}{@{}p{0.78\linewidth}@{\extracolsep{\fill}}r@{}}
    #1 & #2
  \end{tabular*}%
  \ifthenelse{\equal{#3}{}}{%
    \par\vspace{-0.5\parskip}%
  }{%
    \\\noindent\hspace*{0.6em}{\em Current: #3}\par\vspace{-0.7\parskip}%
  }%
}

\def\namesize{\huge}
\def\addressskip{\smallskip}
\def\sectionlineskip{\medskip}
\def\nameskip{\bigskip}
\def\sectionskip{\medskip}
