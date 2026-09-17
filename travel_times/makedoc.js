const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  LevelFormat, ExternalHyperlink,
} = require("docx");

// A4 = 11906 dxa wide. Margins 1080 (0.75in) each side -> content 9746.
const CONTENT = 9746;
const NAVY = "1F3864";
const CODEBG = "F2F2F2";
const WARNBG = "FDECEA";
const NOTEBG = "FFF6E5";
const OKBG = "EAF3EA";

const body = (text, opts = {}) =>
  new Paragraph({
    spacing: { after: 140, line: 276 },
    children: [new TextRun({ text, size: 21, font: "Calibri", ...opts })],
  });

const runs = (children, opts = {}) =>
  new Paragraph({ spacing: { after: 140, line: 276 }, children, ...opts });

const t = (text, opts = {}) => new TextRun({ text, size: 21, font: "Calibri", ...opts });
const mono = (text, opts = {}) => new TextRun({ text, size: 19, font: "Consolas", ...opts });

const h1 = (text) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 340, after: 160 },
    children: [new TextRun({ text, size: 30, bold: true, color: NAVY, font: "Calibri" })],
  });

const h2 = (text) =>
  new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 260, after: 120 },
    children: [new TextRun({ text, size: 24, bold: true, color: NAVY, font: "Calibri" })],
  });

// A command the reader types. One paragraph per line, shaded, monospaced.
const code = (lines, opts = {}) =>
  lines.map((ln, i) =>
    new Paragraph({
      shading: { type: ShadingType.CLEAR, fill: CODEBG },
      spacing: { before: i === 0 ? 60 : 0, after: i === lines.length - 1 ? 160 : 0 },
      indent: { left: 200, right: 200 },
      border: {
        left: { style: BorderStyle.SINGLE, size: 12, color: "BFBFBF", space: 6 },
      },
      children: [mono(ln || " ", opts)],
    })
  );

const bullet = (children) =>
  new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { after: 110, line: 276 },
    children,
  });

// A callout box: single-cell shaded table, so it reads as a distinct block.
const callout = (fill, paragraphs) =>
  new Table({
    columnWidths: [CONTENT],
    width: { size: CONTENT, type: WidthType.DXA },
    rows: [
      new TableRow({
        children: [
          new TableCell({
            width: { size: CONTENT, type: WidthType.DXA },
            shading: { type: ShadingType.CLEAR, fill },
            margins: { top: 160, bottom: 160, left: 220, right: 220 },
            children: paragraphs,
          }),
        ],
      }),
    ],
  });

const spacer = () => new Paragraph({ spacing: { after: 200 }, children: [] });

// ---- troubleshooting table ----
const TROUBLE = [
  ["No module named 'requests' (or 'openpyxl')",
   "Step 2 did not complete. Run: python3 -m pip install --user requests openpyxl"],
  ["Could not import travel_times.py",
   "The files are not all in one folder, or one was renamed when downloaded. Look for travel_times-1.py or travel_times.py.txt and rename it back."],
  ["This file is saved as 'travel_times.py', but it is the KEYLESS companion script",
   "travel_times_free.py was saved over travel_times.py. Extract the zip again into a clean folder."],
  ["Input file not found",
   "The spreadsheet is missing from the folder, or its name changed. It must be exactly Non_Shifters_120_Improved_Approx_Travel_Times.xlsx"],
  ["No contact address set",
   "Step 3 was skipped. Put your email inside the quotes on the CONTACT line."],
  ["A 403, or it stops with a server error",
   "The free services limit heavy use. Wait an hour and run it again. Everything already fetched is cached, so nothing is lost and no requests are repeated."],
];

const COL = [3500, CONTENT - 3500];

const cell = (children, opts = {}) =>
  new TableCell({
    width: { size: opts.w, type: WidthType.DXA },
    margins: { top: 90, bottom: 90, left: 130, right: 130 },
    shading: opts.fill ? { type: ShadingType.CLEAR, fill: opts.fill } : undefined,
    children,
  });

const troubleTable = new Table({
  columnWidths: COL,
  width: { size: CONTENT, type: WidthType.DXA },
  rows: [
    new TableRow({
      tableHeader: true,
      children: [
        cell([new Paragraph({ children: [new TextRun({ text: "If you see this", bold: true, color: "FFFFFF", size: 20, font: "Calibri" })] })], { w: COL[0], fill: NAVY }),
        cell([new Paragraph({ children: [new TextRun({ text: "Do this", bold: true, color: "FFFFFF", size: 20, font: "Calibri" })] })], { w: COL[1], fill: NAVY }),
      ],
    }),
    ...TROUBLE.map(([a, b], i) =>
      new TableRow({
        children: [
          cell([new Paragraph({ children: [mono(a, { size: 17 })] })], { w: COL[0], fill: i % 2 ? "F7F7F7" : undefined }),
          cell([new Paragraph({ children: [t(b, { size: 19 })] })], { w: COL[1], fill: i % 2 ? "F7F7F7" : undefined }),
        ],
      })
    ),
  ],
});

// ---- comparison table ----
const CCOL = [2600, 3573, 3573];
const compareTable = new Table({
  columnWidths: CCOL,
  width: { size: CONTENT, type: WidthType.DXA },
  rows: [
    new TableRow({
      tableHeader: true,
      children: [
        cell([new Paragraph({ children: [new TextRun({ text: "", bold: true, color: "FFFFFF", size: 20, font: "Calibri" })] })], { w: CCOL[0], fill: NAVY }),
        cell([new Paragraph({ children: [new TextRun({ text: "travel_times_free.py", bold: true, color: "FFFFFF", size: 19, font: "Consolas" })] })], { w: CCOL[1], fill: NAVY }),
        cell([new Paragraph({ children: [new TextRun({ text: "travel_times.py", bold: true, color: "FFFFFF", size: 19, font: "Consolas" })] })], { w: CCOL[2], fill: NAVY }),
      ],
    }),
    ...[
      ["API key", "None needed", "Free TomTom key, email signup, no credit card"],
      ["Traffic", "None. Free-flow times only", "Yes, and a chosen departure time can be modelled"],
      ["Traffic delay column", "Not produced", "Produced"],
      ["Place lookup quality", "Weaker, so every match is logged for you to audit", "Stronger"],
      ["Run time", "About 4 minutes", "About 2 minutes"],
      ["Use it for", "Testing the setup, trip distances, free-flow times", "Anything published"],
    ].map(([a, b, c], i) =>
      new TableRow({
        children: [
          cell([new Paragraph({ children: [t(a, { bold: true, size: 19 })] })], { w: CCOL[0], fill: i % 2 ? "F7F7F7" : undefined }),
          cell([new Paragraph({ children: [t(b, { size: 19 })] })], { w: CCOL[1], fill: i % 2 ? "F7F7F7" : undefined }),
          cell([new Paragraph({ children: [t(c, { size: 19 })] })], { w: CCOL[2], fill: i % 2 ? "F7F7F7" : undefined }),
        ],
      })
    ),
  ],
});

const doc = new Document({
  creator: "CEEW",
  title: "How to Use - Bengaluru Travel Times Scripts",
  description: "Setup and run instructions for the BBUS non-shifters travel time scripts.",
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [
          {
            level: 0,
            format: LevelFormat.BULLET,
            text: "•",
            alignment: AlignmentType.LEFT,
            style: { paragraph: { indent: { left: 360, hanging: 240 } } },
          },
        ],
      },
    ],
  },
  sections: [
    {
      properties: { page: { margin: { top: 1080, bottom: 1080, left: 1080, right: 1080 } } },
      children: [
        // ---------------- title ----------------
        new Paragraph({
          spacing: { after: 60 },
          children: [new TextRun({ text: "How to use these scripts", size: 40, bold: true, color: NAVY, font: "Calibri" })],
        }),
        new Paragraph({
          spacing: { after: 240 },
          border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: NAVY, space: 8 } },
          children: [new TextRun({ text: "Bengaluru travel times  |  non-shifters origin-destination file  |  120 respondents", size: 21, color: "595959", font: "Calibri" })],
        }),

        body("These scripts estimate travel times between each survey respondent's home area and work area, and fill three columns: 2-Wheeler, Bus and Auto/Cab."),

        callout(OKBG, [
          new Paragraph({ spacing: { after: 80 }, children: [t("You need to change one thing: your email address, in Step 3.", { bold: true, size: 22 })] }),
          new Paragraph({ children: [t("There are no file paths to edit. Keep all the files in one folder, put that folder anywhere you like, and everything finds itself.", { size: 20 })] }),
        ]),
        spacer(),

        // ---------------- what's in the folder ----------------
        h1("What is in the folder"),
        bullet([mono("README_FIRST.txt", { bold: true }), t("  and  "), mono("How_to_use.docx", { bold: true }), t("  - this guidance, in two formats.")]),
        bullet([mono("travel_times_free.py", { bold: true }), t("  - "), t("start here.", { bold: true }), t(" Needs no API key.")]),
        bullet([mono("travel_times.py"), t("  - a better version that accounts for traffic, but needs a free API key. Optional.")]),
        bullet([mono("resolve_places.py"), t("  - helps identify the 12 area names that could not be matched. Also needs the key. Optional.")]),
        bullet([mono("Non_Shifters_120_Improved_Approx_Travel_Times.xlsx"), t("  - the survey data the scripts read.")]),
        body("The three scripts share one list of place names, held in travel_times.py, so a name corrected once is corrected for all of them. That is why they must stay in the same folder."),

        // ---------------- step 1 ----------------
        h1("Step 1  ·  Check you have Python"),
        body("Open Terminal. On a Mac, press Cmd+Space, type Terminal, press Enter. Then type:"),
        ...code(["python3 --version"]),
        body("Anything from 3.9 upwards is fine. If it says \"command not found\", install Python from python.org/downloads and then close and re-open Terminal."),

        // ---------------- step 2 ----------------
        h1("Step 2  ·  Install the two libraries"),
        body("Once only, on this computer:"),
        ...code(["python3 -m pip install requests openpyxl"]),

        // ---------------- step 3 ----------------
        h1("Step 3  ·  Put your email in the script"),
        runs([t("Open "), mono("travel_times_free.py"), t(" in any text editor. Near the top you will find this line:")]),
        ...code(['CONTACT = ""']),
        body("Put your work email between the quotation marks, and save the file:"),
        ...code(['CONTACT = "your.name@yourorg.com"']),
        callout(NOTEBG, [
          new Paragraph({ spacing: { after: 80 }, children: [t("This is not a signup, and nothing is sent to us.", { bold: true, size: 20 })] }),
          new Paragraph({ children: [t("The free service that looks up place names (Nominatim, run by OpenStreetMap volunteers on donated infrastructure) requires scripts to identify who is calling, so they can get in touch if a script misbehaves. It is a condition of using the service, not an optional courtesy. The script will stop and remind you if you skip it.", { size: 20 })] }),
        ]),
        spacer(),

        // ---------------- step 4 ----------------
        h1("Step 4  ·  Run it"),
        body("First, move Terminal into the folder. Type cd followed by a space, then drag the folder from Finder into the Terminal window and press Enter. That fills in the path for you, so there is nothing to type or spell:"),
        ...code(["cd ", "   (now drag the folder in, then press Enter)"]),
        body("Now check the setup without using the internet at all. This makes no requests and writes nothing:"),
        ...code(["python3 travel_times_free.py --dry-run"]),
        body("You should see these three lines:"),
        ...code(["respondents        120", "ready to route     108", "need your decision 12"]),
        body("If you see that, the setup is correct. Now run it properly:"),
        ...code(["python3 travel_times_free.py"]),
        runs([t("It takes about four minutes and prints its progress as it goes. When it finishes you will have a new file in the folder: "), mono("Travel_Times_FILLED_free.xlsx"), t(".")]),
        callout(NOTEBG, [
          new Paragraph({ children: [t("It runs slowly on purpose. The free services allow only one request per second, and that limit is a condition of access - please do not try to speed it up. Everything is cached as it goes, so if it stops partway, simply run it again: it picks up where it left off and repeats no requests.", { size: 20 })] }),
        ]),
        spacer(),

        // ---------------- caveats ----------------
        h1("Before you use any number from the output"),
        body("These are not small print. They change what the figures can honestly be used for, and they should travel with the numbers into any note, slide or table built from them."),

        callout(WARNBG, [
          new Paragraph({ spacing: { after: 80 }, children: [t("There is no traffic in these times.", { bold: true, size: 22 })] }),
          new Paragraph({ spacing: { after: 80 }, children: [t("Every figure the keyless script produces is a free-flow time: how long the trip would take on empty roads. The free routing service has no congestion data at all.", { size: 20 })] }),
          new Paragraph({ children: [t("For Bengaluru this understates real peak-hour travel substantially, and it does so unevenly - a congested arterial is hit far harder than a quiet side road, so you cannot correct it by multiplying everything by a single factor. Do not present any figure from this version as a peak-hour or typical-commute time.", { size: 20 })] }),
        ]),
        spacer(),

        h2("The Bus column is not a bus journey time"),
        body("It is in-vehicle road time for a bus-sized vehicle. It excludes waiting for the bus, time spent at stops, and transfers, which are often the majority of a real bus trip. A true BMTC journey time needs BMTC route and headway (GTFS) data. Please do not label this column as bus journey time."),

        h2("The Auto/Cab column is a proxy"),
        body("No routing service has an auto-rickshaw mode. This column uses the motorcycle mode with its top speed capped at 45 km/h. That cap is an assumption, not a measurement. Car time is given in its own column so you can see how much the choice of mode moves the number. If you use this figure, state the assumption."),

        h2("Every trip runs between area centres"),
        body("The survey recorded areas, not addresses, so each trip goes from the centre of one locality to the centre of another. Trips under 3 km are flagged in the Status column, because over such a short distance the error introduced by using area centres is a large share of the whole trip."),

        h2("Read the Geocoding sheet"),
        body("It records which real place the service matched for each of the 66 area names, and how far that is from the city centre. Every number in the workbook depends on those 66 points, so one wrong match is a wrong travel time everywhere it appears. Rows worth a second look are highlighted, but only your eye will catch a match that looks plausible and is still wrong."),

        h2("Twelve rows are left blank on purpose"),
        body("Twelve respondents recorded an area name that could not be identified with confidence. Some are unclear spellings; four name an employer or institution with many Bengaluru sites - Infosys, a bank branch, a training institute, an electricity board office - rather than a place. The script leaves these blank rather than guessing, and lists them on the Needs review sheet. A blank is a defensible result; a guess is not."),

        // ---------------- optional scripts ----------------
        h1("The other two scripts"),
        body("Both need a free TomTom key: sign up with an email address at developer.tomtom.com, no credit card. Paste the key into the API_KEY line near the top of the script."),

        h2("travel_times.py  -  the traffic-aware version"),
        body("Same three columns, but it accounts for congestion, which is a real improvement on the keyless version. It can also model a specific departure time:"),
        ...code(["python3 travel_times.py", "python3 travel_times.py --depart 2026-09-21T09:00:00+05:30"]),

        h2("resolve_places.py  -  clearing the twelve blanks"),
        body("It asks TomTom what real places match each unidentified name, and reports the candidates with a match score, the kind of place, and - most usefully - how far each candidate sits from the other end of that person's commute. A candidate 80 km from a daily commute is almost certainly wrong."),
        ...code(["python3 resolve_places.py"]),
        body("It proposes; you decide. It never edits anything by itself. Accepting a candidate means pasting the line it gives you into travel_times.py and running the main script again."),

        h2("Which version to use"),
        compareTable,
        spacer(),

        // ---------------- trouble ----------------
        h1("If something goes wrong"),
        troubleTable,
        spacer(),

        // ---------------- attribution ----------------
        h1("Credit where it is due"),
        body("Both engines require attribution, and it belongs in the methodology of anything published from these numbers, alongside which version produced them."),
        bullet([t("Keyless version: place lookup © OpenStreetMap contributors, ODbL. Routing by Valhalla on FOSSGIS infrastructure, using OpenStreetMap data.")]),
        bullet([t("TomTom version: routing, traffic and geocoding data © TomTom.")]),
        new Paragraph({
          spacing: { before: 300 },
          border: { top: { style: BorderStyle.SINGLE, size: 8, color: "BFBFBF", space: 8 } },
          children: [t("These are estimates produced from area centres, not measured trips. Check them against something you know before they inform a finding.", { italics: true, size: 19, color: "595959" })],
        }),
      ],
    },
  ],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(process.argv[2] || "How_to_use.docx", buf);
  console.log("written:", process.argv[2] || "How_to_use.docx", buf.length, "bytes");
});
