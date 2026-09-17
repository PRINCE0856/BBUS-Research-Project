===============================================================================
 BENGALURU TRAVEL TIMES  -  START HERE
===============================================================================

 Fills three travel-time columns (2-Wheeler, Bus, Auto/Cab) for 120 survey
 respondents, from their recorded home and work areas.

 THE SAME INSTRUCTIONS ARE IN "How_to_use.docx" IN THIS FOLDER, formatted for
 reading on screen or printing. Open whichever you prefer - the content is the
 same. This plain-text version is here because it opens on any machine, with
 no Word needed.

 YOU NEED TO CHANGE ONE THING: your email address, in step 3 below.
 Nothing else. No file paths to edit.

 Keep all five files in the SAME FOLDER. Move the folder wherever you like -
 Desktop, Documents, anywhere. The scripts find each other and the spreadsheet
 on their own, and work from any folder.


-------------------------------------------------------------------------------
 STEP 1  -  Check you have Python
-------------------------------------------------------------------------------

 Open Terminal (Mac: press Cmd+Space, type "Terminal", press Enter) and run:

     python3 --version

 Anything 3.9 or higher is fine. If it says "command not found", install
 Python from https://www.python.org/downloads/ and then re-open Terminal.


-------------------------------------------------------------------------------
 STEP 2  -  Install the two libraries (once only)
-------------------------------------------------------------------------------

     python3 -m pip install requests openpyxl


-------------------------------------------------------------------------------
 STEP 3  -  Put your email in travel_times_free.py
-------------------------------------------------------------------------------

 Open travel_times_free.py in any text editor. Near the top you will find:

     CONTACT = ""

 Put your work email between the quotes:

     CONTACT = "yourname@yourorg.com"

 Save the file.

 This is NOT a signup. The free map service used for looking up places
 (Nominatim, run by OpenStreetMap volunteers) requires scripts to identify
 who is calling, so they can get in touch if a script misbehaves. It is a
 condition of using the service. The script will stop and remind you if you
 skip this.


-------------------------------------------------------------------------------
 STEP 4  -  Run it
-------------------------------------------------------------------------------

 In Terminal, type "cd " (c, d, space) then DRAG THE FOLDER from Finder into
 the Terminal window and press Enter. That moves Terminal into the folder
 without you having to type the path.

 Then check the wiring without using the internet at all:

     python3 travel_times_free.py --dry-run

 You should see:

     respondents        120
     ready to route     108
     need your decision 12

 If you see that, you are set up correctly. Now run it for real:

     python3 travel_times_free.py

 It takes about 4 minutes. It deliberately goes slowly, because the free
 services it uses allow only one request per second and that limit is a
 condition of access - please do not speed it up. Everything is cached, so if
 it stops partway, running it again picks up where it left off and costs no
 repeat requests.

 When it finishes you will have:

     Travel_Times_FILLED_free.xlsx


-------------------------------------------------------------------------------
 WHAT YOU GET, AND WHAT IT DOES NOT MEAN
-------------------------------------------------------------------------------

 Please read this before using any number from the output. These are not
 small print - they change what the figures can honestly be used for.

 NO TRAFFIC.  Every time in the output is a FREE-FLOW time: how long the trip
 would take on empty roads. The free routing service has no congestion data at
 all. For Bengaluru this understates real peak-hour travel substantially, and
 it does so UNEVENLY - a congested arterial is hit far harder than a quiet
 side road, so you cannot correct it by multiplying everything by a factor.
 Do not present any figure here as a peak-hour or typical-commute time.

 BUS IS NOT A BUS JOURNEY TIME.  The Bus column is in-vehicle road time for a
 bus-sized vehicle. It EXCLUDES waiting for the bus, time spent at stops, and
 transfers - which are often the majority of a real bus trip. A true BMTC
 journey time needs BMTC route and headway (GTFS) data. Do not label this
 column as bus journey time.

 AUTO/CAB IS A PROXY.  No routing service has an auto-rickshaw mode. This
 column is the motorcycle mode with its top speed capped at 45 km/h. That cap
 is an ASSUMPTION, not a measurement. Car time is given in its own column so
 you can see how much the choice of mode moves the number.

 EVERY TRIP IS BETWEEN AREA CENTRES.  The survey recorded areas, not
 addresses, so each trip runs from the centre of one locality to the centre of
 another. Trips under 3 km are flagged, because over such a short distance the
 error from using area centres is a large share of the trip.

 CHECK THE "Geocoding" SHEET.  It records which real place the service matched
 for each of the 66 area names, and how far that is from the city centre.
 Every number in the file depends on those 66 points, so one wrong match is a
 wrong travel time everywhere it appears. Rows worth a second look are
 highlighted. This sheet is there to be read.

 12 ROWS ARE LEFT BLANK ON PURPOSE.  Twelve respondents recorded an area name
 that could not be identified with confidence - some are unclear spellings,
 and four name an employer with many Bengaluru sites (Infosys, a bank branch,
 a training institute, an electricity board office) rather than a place. The
 script leaves these blank rather than guessing. They are listed on the
 "Needs review" sheet. A blank is a defensible result; a guess is not.


-------------------------------------------------------------------------------
 THE OTHER TWO SCRIPTS  -  optional, and they need a free API key
-------------------------------------------------------------------------------

 travel_times.py     Same three columns, but TRAFFIC-AWARE, which is a real
                     improvement on the above. Needs a free TomTom key (email
                     signup, no credit card): https://developer.tomtom.com/
                     Paste it into API_KEY near the top, then:
                         python3 travel_times.py
                     Also lets you model a chosen departure time:
                         python3 travel_times.py --depart 2026-09-21T09:00:00+05:30

 resolve_places.py   Helps clear the 12 unidentified area names. It asks
                     TomTom what real places match each one and reports the
                     candidates with a match score and, most usefully, how far
                     each candidate sits from the other end of that person's
                     commute. Also needs the TomTom key.
                         python3 resolve_places.py
                     It proposes; you decide. It never edits anything itself.

 Both read their list of place names from travel_times.py, so all three
 scripts must stay in the same folder and a name fixed once is fixed for all.


-------------------------------------------------------------------------------
 IF SOMETHING GOES WRONG
-------------------------------------------------------------------------------

 "No module named requests" / "openpyxl"
     Step 2 did not run. Try:  python3 -m pip install --user requests openpyxl

 "Could not import travel_times.py"
     The files are not in the same folder, or one was renamed on download
     (check for travel_times-1.py or travel_times.py.txt and rename it back).

 "Input file not found"
     The .xlsx is not in the folder with the scripts, or its name changed.
     It must be exactly:
         Non_Shifters_120_Improved_Approx_Travel_Times.xlsx

 "No contact address set"
     Step 3 was skipped.

 A 403, or it stops with a server error
     The free services throttle heavy use. Wait an hour and run it again -
     the cache keeps everything already fetched, so nothing is lost.


-------------------------------------------------------------------------------
 ATTRIBUTION
-------------------------------------------------------------------------------

 Keyless version: place lookup (c) OpenStreetMap contributors, ODbL. Routing
 by Valhalla on FOSSGIS infrastructure, using OpenStreetMap data.
 TomTom version: routing, traffic and geocoding data (c) TomTom.
 Credit whichever you used, and name it in your methodology, in anything you
 publish from these numbers.
