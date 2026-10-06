MECHAGOTCHI - WINDOWS X64 PLAYER

Double-click Mechagotchi.exe to open the startup window. Keep this entire
folder together: the executable needs its adjacent _internal folder.

START OR CONTINUE
Startup shows the selected save directory and the available choices.
Resume continues that saved companion. Inspect backup lets you read a backup
before choosing Restore. Restore and New companion require a separate
confirmation that starts on Cancel. Choose save directory lets you type a
different path; cancel keeps your current selection. Retry refreshes inspection.

Your usual save home is .mechagotchi inside your Windows user folder, for example
C:\Users\YOURNAME\.mechagotchi. An older save in _internal\keeper is continued
in place only when the user-folder save home has no existing save. If both have
saves, the user-folder home takes priority. Neither location is silently moved.
You can select another home in startup or launch with an explicit path:

  .\Mechagotchi.exe --keeper-dir "C:\path\to\your\keeper"

CHOOSE HOW A NEW LIFE LEARNS
Fresh Keepers using the packaged starting inputs use Q-table learning. In the
New companion confirmation, New policy switches between Q-table and incumbent
before you create the life. Existing Keepers keep their saved choice by default.
Resume never changes that choice. Each new life starts without a trained table;
quitting and returning preserves the current life's learning.

Only you can feed your companion. Learning improved average welfare in the
measured standard-care cohort; it did not prevent deaths under neglect.
Custom seed or covenant options default to incumbent unless you choose otherwise.

OPTIONAL BODY RESPONSE
New companion includes a Body choice. Legacy remains the default. The experimental
workload-v1 option makes Play energy follow the actual body's functional support
and mass. Current care, Keeper lives, next-era preparation and recorded era review
show the chosen model; page through the footer for the play energy cost.

An explicit new-life launch is also available:

  .\Mechagotchi.exe --keeper-dir "C:\path\to\new-keeper" --new --body-response workload-v1

Resume and recovery keep the saved model. Existing campaigns retain their model;
choose a separate Keeper directory to begin a campaign under a different model.
Successors recompute their cost from their own body and start without a trained
Q-table. The prior learning welfare result used the original physiology and does
not establish a benefit for workload-v1. Food, repair and death rules are unchanged.

FIND YOUR WAY
F1 opens contextual help. F6 focuses the visible actions; use arrows or Tab
to move between them and Enter or Space to activate. You can also click actions.
The available actions follow the current care, preparation, era or reading view.

J opens Workshop for the selected Keeper in your browser. Keep Mechagotchi open
while using Workshop: its local server belongs to the application and closes
when the application exits. The creator view shows the address and lets you
reopen the browser. Return to care with J or Escape.

REVIEW AND REPRODUCE AN ERA
T opens recorded era review; B opens its archive. Review shows release occurrences
in submission order, their recorded admission decisions and available source labels.
New eras retain their inputs. Older eras remain readable and say when those inputs
were not recorded. Recorded evaluation links, declared ancestry and cared lives
remain separate facts.

Choose Reproduce [D] in era or archive review to compare the selected era against
its retained inputs. Care pauses during the comparison. Escape cancels; the result
reports a match, mismatch or why reproduction is unavailable. Original results and
recordings are preserved. Opening a review never starts a comparison automatically.

An explicit PowerShell comparison can also save its results to a new directory:

  .\Mechagotchi.exe --keeper-dir "C:\path\to\your\keeper" --campaign-id "RECORDED_ID" --reproduce-era 0 --output "C:\path\to\new-comparison"

Use the campaign identity shown in era review and a directory outside your Keeper.
The command exits with 0 for a match, 1 for a mismatch and 2 when unavailable.

OPTIONAL EXAMPLE
From PowerShell in this folder, run the isolated care-to-era example:

  .\Mechagotchi.exe --example care-to-era --output "$env:USERPROFILE\Mechagotchi-example-new"

Choose an output directory that does not already exist. The example creates its
own saved companion and report there; its small verification run is not a
scientific performance result.

EARNED PREPARATION AND INTERRUPTED SAVES
C opens the covenant view. Before the first era, Start with role limits [9]
selects the experimental living-generations campaign with four starting roles.
Existing campaigns keep their recorded population policy. The ordinary default
continues to use archive continuity.

The covenant view lists active roles and whether the next role is locked or
ready. Spend organ role [5] adds one earned role per fresh press: ornament at
niche mastery tier 1 (16 niches), then effect at tier 2 (26 niches). Density [6]
requires the saved storm-record unlock. These choices are explicit; earning a
permission does not spend it. Page through the footer to read the next era's
weather, population policy, survival setting, density and staged contributions.
Return with C; E runs the prepared era. Covenant view continues companion care;
recorded era and archive views pause care.

If a preparation save is interrupted, the application retains the captured
choice and shows that it awaits finishing. In the covenant view, Finish saved
preparation [E] completes that same choice without another spend or era. A fresh
Enter can finish the same captured import while its unchanged inbox remains
open. On restart, use the covenant action or this explicit command:

  .\Mechagotchi.exe --keeper-dir "C:\path\to\your\keeper" --finish-preparation

If the captured choice cannot be read, inspect the paired checkpoint before
choosing recovery. Do not delete the journal or replace saved files by hand.
Recovery preserves the superseded captured choice as evidence.

NOTICES
Project license: _internal\LICENSE
Installed dependency notices: _internal\notices
Tagged pygame/SDL notices: _internal\game\notices\pygame-ce-2.5.7
