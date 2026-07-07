/**
 * @brief Folder Down Navigation
 * Browses into the Next folder or displays file name.
 *
 * @param dir The directory to read from
 */
void folderDown(File dir) {
  counter++;  
  for (int i = 0; i < counter; i++) {
    while (true) {
      File entry =  dir.openNextFile();     
      if (! entry) {
        counter--;
        break;
      }
      if (entry.isDirectory()) {
        char foldertest[101];
        entry.getName(foldertest, 101);
        FileName = foldertest;
        FileName += "/1.png";
        File entry2 = SD.open(FileName);
        if (entry2){
          entry.getName(foldersel_long, 101);
          break;  
        }  
      }
      entry.close();
    }
  } 
    foldersel = String(foldersel_long);
    foldersel = foldersel.substring(0, 10);
    gfx2->fillRoundRect(7, 28, 137, 22, 2, BLACK);
    gfx2->setFont(&FreeSans8pt7b);
    gfx2->setTextColor(WHITE);
    gfx2->setTextSize(1);
    gfx2->setCursor(12, 43);
    gfx2->print(foldersel);  
}
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



/**
 * @brief Folder Up Navigation
 * Browses to the Previous folder.
 *
 * @param dir The directory to read from
 */
void folderUp(File dir) {
  if (counter > 1) {
    counter --;
    for (int i = 0; i < counter; i++) {
      while (true) {
        File entry =  dir.openNextFile();
        /*if (! entry) {
          break;
        }*/
        if (entry.isDirectory()) {
          entry.getName(foldersel_long, 101);
          FileName = foldersel_long;
          FileName += "/1.png";
          File entry2 = SD.open(FileName);
          if (entry2)
            break;
        }
        entry.close();
      }
    }  
    foldersel = String(foldersel_long);
    foldersel = foldersel.substring(0, 10);
    gfx2->fillRoundRect(7, 28, 137, 22, 2, BLACK);
    gfx2->setFont(&FreeSans8pt7b);
    gfx2->setTextColor(WHITE);
    gfx2->setTextSize(1);
    gfx2->setCursor(12, 43);
    gfx2->print(foldersel);
  }
}
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

/**
 * @brief Delete a model folder from SD: removes all files inside, then the
 * folder itself. Used by the long-press-OK delete feature in the Print menu.
 */
bool deleteModelFolder(const char *path) {
  // Pass 1: count entries (deleting hundreds of layer PNGs takes tens of
  // seconds on FAT, so we show a progress bar like the WiFi connect one)
  File dir = SD.open(path);
  if (!dir) return false;
  int total = 0;
  while (true) {
    File entry = dir.openNextFile();
    if (!entry) break;
    total++;
    entry.close();
  }
  dir.close();
  if (total == 0) return SD.rmdir(path);

  // Pass 2: delete with progress
  dir = SD.open(path);
  if (!dir) return false;
  int done = 0;
  while (true) {
    File entry = dir.openNextFile();
    if (!entry) break;
    char name[101];
    entry.getName(name, sizeof(name));
    bool isDir = entry.isDirectory();
    entry.close();
    String full = String(path) + "/" + String(name);
    if (isDir) SD.rmdir(full.c_str());
    else SD.remove(full.c_str());
    done++;
    if (done % 10 == 0 || done == total) {
      int w = (int)(136L * done / total);
      if (w > 136) w = 136;
      if (w > 0) gfx2->fillRect(12, 50, w, 12, ORANGE);
    }
  }
  dir.close();
  return SD.rmdir(path);
}

/**
 * @brief Screen 113: delete confirmation for the selected model.
 * OK = delete (handled in loop), Back = return to the model list.
 */
void screenDeleteConfirm(){
  gfx2->fillScreen(BLACK);
  gfx2->fillRoundRect(0, 0, 160, 80, 5, ORANGE);
  gfx2->fillRoundRect(2, 2, 156, 76, 3, BLACK);
  gfx2->setFont(&FreeSans8pt7b);
  gfx2->setTextColor(WHITE);
  gfx2->setTextSize(1);
  gfx2->setCursor(8, 20);
  gfx2->print("Delete model?");
  gfx2->setTextColor(ORANGE);
  gfx2->setCursor(8, 44);
  gfx2->print(foldersel);
  gfx2->setTextColor(WHITE);
  gfx2->setCursor(8, 70);
  gfx2->print("OK=Yes  Back=No");
  screen = 113;
}

/**
 * @brief Deletes the currently selected model folder and returns to Main Menu.
 */
void deleteSelectedModel(){
  gfx2->fillScreen(BLACK);
  gfx2->setFont(&FreeSans8pt7b);
  gfx2->setTextColor(WHITE);
  gfx2->setTextSize(1);
  gfx2->setCursor(5, 18);
  gfx2->print("Deleting:");
  gfx2->setCursor(5, 38);
  gfx2->print(foldersel);
  gfx2->drawRoundRect(10, 48, 140, 16, 3, WHITE);
  String path = "/" + String(foldersel_long);
  bool ok = deleteModelFolder(path.c_str());
  gfx2->fillScreen(BLACK);
  gfx2->setFont(&FreeSans8pt7b);
  gfx2->setTextColor(WHITE);
  gfx2->setCursor(8, 44);
  gfx2->print(ok ? "Deleted" : "Delete FAILED");
  delay(1200);
  screen1();
}
