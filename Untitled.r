# ============================================================
# Amritsar Survey — Access & Egress Distance Regression Models
# ============================================================

# ---- 1. Packages ----
# Run these once if not already installed:
# install.packages(c("readxl", "dplyr", "broom"))
library(readxl)
library(dplyr)
library(broom)

# ---- 2. Load data ----
# Row 1 = full question text, Row 2 = short codes -> skip = 1 makes row 2 the header
file_path <- "/Users/princek.patel/Desktop/CEEW/Work/UM- Amrtisar survey data analysis- 20Nov25.xlsx"

df_raw <- read_excel(
  file_path,
  sheet = "Cleaned Amritsar Main Data",
  skip = 1
)

cat("Rows loaded:", nrow(df_raw), " | Columns loaded:", ncol(df_raw), "\n")

# ---- 3. Select, rename, and type variables ----
df <- df_raw %>%
  select(
    mode        = od_q_10,     # Shared Autorickshaw / Shared E-Rickshaw / Two Wheeler / Bicycle / Private E-Rickshaw
    gender      = od_q_5,
    age         = od_q_6,      # continuous
    profession  = od_q_7,
    purpose     = od_q_9,      # trip purpose
    trips_week  = od_q_11,     # continuous
    access_m    = od_q_18,
    egress_m    = od_q_21
  ) %>%
  mutate(
    age           = as.numeric(age),
    trips_week    = as.numeric(trips_week),
    access_m      = as.numeric(access_m),
    egress_m      = as.numeric(egress_m),
    access_egress = access_m + egress_m,     # dependent variable (sum of access + egress, in metres)
    gender        = factor(gender),
    profession    = factor(profession),
    purpose       = factor(purpose)
  ) %>%
  filter(
    !is.na(mode), !is.na(gender), !is.na(age), !is.na(profession),
    !is.na(purpose), !is.na(trips_week), !is.na(access_egress)
  )

cat("Total cleaned rows:", nrow(df), "\n")
cat("Mode breakdown:\n")
print(table(df$mode))


# ============================================================
# MODEL SET 1 — Three separate models, one per mode
# ============================================================

run_mode_model <- function(mode_name, data) {
  sub <- data %>% filter(mode == mode_name)
  model <- lm(
    access_egress ~ age + trips_week + gender + profession + purpose,
    data = sub
  )
  cat("\n============================================\n")
  cat(mode_name, " | n =", nrow(sub), "\n")
  cat("============================================\n")
  print(summary(model))
  return(model)
}

model_autorickshaw <- run_mode_model("Shared Autorickshaw", df)
model_erickshaw    <- run_mode_model("Shared E-Rickshaw", df)
model_twowheeler   <- run_mode_model("Two Wheeler", df)

# Tidy coefficient tables
tidy_autorickshaw <- tidy(model_autorickshaw)
tidy_erickshaw    <- tidy(model_erickshaw)
tidy_twowheeler   <- tidy(model_twowheeler)


# ============================================================
# MODEL SET 2 — Combined binary mode-group model
# Rickshaw (Shared Autorickshaw + Shared E-Rickshaw) vs Two Wheeler
# Bicycle and Private E-Rickshaw are dropped
# ============================================================

df_binary <- df %>%
  filter(mode %in% c("Shared Autorickshaw", "Shared E-Rickshaw", "Two Wheeler")) %>%
  mutate(
    mode_group = case_when(
      mode %in% c("Shared Autorickshaw", "Shared E-Rickshaw") ~ "Rickshaw",
      mode == "Two Wheeler" ~ "Two Wheeler"
    ),
    mode_group = factor(mode_group, levels = c("Two Wheeler", "Rickshaw"))
    # reference level = "Two Wheeler"
  )

cat("\nMode group counts (binary model):\n")
print(table(df_binary$mode_group))

model_binary <- lm(
  access_egress ~ age + trips_week + gender + profession + purpose + mode_group,
  data = df_binary
)

cat("\n============================================\n")
cat("Combined Binary Mode-Group Model | n =", nrow(df_binary), "\n")
cat("============================================\n")
print(summary(model_binary))

tidy_binary <- tidy(model_binary)


#####################
#####################
#####################




# ============================================================
# Amritsar Survey — Binary Mode Model (Rickshaw vs Two Wheeler)
# Rows kept: Shared Autorickshaw + Shared E-Rickshaw + Two Wheeler ONLY
# All other modes (Bicycle, Private E-Rickshaw) removed
# Dependent variable: access_egress (access + egress distance, metres)
# Independent variables:
#   - mode_group (binary: Rickshaw vs Two Wheeler)
#   - age (continuous)
#   - gender (categorical)
#   - purpose_group (BINARY: Work vs Other)
#   - od_time_bin (BINARY: <=10 min = 1)
#   - od_fare_bin (BINARY: <=10 = 1)
#   - od_distance_bin (BINARY: <=5 km = 1)
#   - trips_week_bin (BINARY: >=5 per week = 1)
#   - own_2w (BINARY: 0 = owns none, 1 = owns one or more)
#   - own_4w (BINARY: 0 = owns none, 1 = owns one or more)
# (profession removed)
# ============================================================
# ---- 1. Packages ----
library(readxl)
library(dplyr)
library(broom)
# ---- 2. Load data ----
file_path <- "/Users/princek.patel/Desktop/CEEW/Work/UM- Amrtisar survey data analysis- 20Nov25.xlsx"
df_raw <- read_excel(
  file_path,
  sheet = "Cleaned Amritsar Main Data",
  skip = 1
)
cat("Rows loaded:", nrow(df_raw), " | Columns loaded:", ncol(df_raw), "\n")
# ---- 3. Keep only the three relevant modes, build all variables ----
df_binary <- df_raw %>%
  select(
    mode        = od_q_10,
    gender      = od_q_5,
    age         = od_q_6,
    own_2w_raw  = od_q_8_1_2W,
    own_4w_raw  = od_q_8_2_4W,
    purpose_raw = od_q_9,
    trips_week  = od_q_11,
    od_distance = od_q_14,
    od_time     = od_q_15,
    od_fare     = od_q_16,
    access_m    = od_q_18,
    egress_m    = od_q_21
  ) %>%
  mutate(
    age           = as.numeric(age),
    trips_week    = as.numeric(trips_week),
    od_distance   = as.numeric(od_distance),
    od_time       = as.numeric(od_time),
    od_fare       = as.numeric(od_fare),
    access_m      = as.numeric(access_m),
    egress_m      = as.numeric(egress_m),
    access_egress = access_m + egress_m,
    gender        = factor(gender),
    
    own_2w_raw    = as.numeric(own_2w_raw),
    own_4w_raw    = as.numeric(own_4w_raw),
    own_2w        = factor(if_else(own_2w_raw >= 1, "Yes", "No"), levels = c("No", "Yes")),
    own_4w        = factor(if_else(own_4w_raw >= 1, "Yes", "No"), levels = c("No", "Yes")),
    
    # ---- Trip purpose collapsed to binary: Work vs Other ----
    purpose_group = case_when(
      purpose_raw == "Work" ~ "Work",
      TRUE ~ "Other"
    ),
    purpose_group = factor(purpose_group, levels = c("Other", "Work")),
    
    # ---- Trips per week binary: >=5 = "High", else "Low" ----
    trips_week_bin = factor(if_else(trips_week >= 5, "High", "Low"), levels = c("Low", "High")),
    
    # ---- OD distance binary: <=5 km = "Short", else "Long" ----
    od_distance_bin = factor(if_else(od_distance <= 5, "Short", "Long"), levels = c("Long", "Short")),
    
    # ---- OD fare binary: <=10 = "Low", else "High" ----
    od_fare_bin = factor(if_else(od_fare <= 10, "Low", "High"), levels = c("High", "Low")),
    
    # ---- OD time binary: <=10 min = "Short", else "Long" ----
    od_time_bin = factor(if_else(od_time <= 10, "Short", "Long"), levels = c("Long", "Short"))
  ) %>%
  filter(mode %in% c("Shared Autorickshaw", "Shared E-Rickshaw", "Two Wheeler")) %>%
  mutate(
    mode_group = case_when(
      mode %in% c("Shared Autorickshaw", "Shared E-Rickshaw") ~ "Rickshaw",
      mode == "Two Wheeler" ~ "Two Wheeler"
    ),
    mode_group = factor(mode_group, levels = c("Two Wheeler", "Rickshaw"))
  ) %>%
  filter(
    !is.na(access_egress), !is.na(mode_group),
    !is.na(gender), !is.na(age),
    !is.na(own_2w), !is.na(own_4w),
    !is.na(purpose_group),
    !is.na(trips_week_bin), !is.na(od_distance_bin),
    !is.na(od_time_bin), !is.na(od_fare_bin)
  )
cat("\nMode group counts:\n")
print(table(df_binary$mode_group))
cat("\n2W ownership (binary):\n")
print(table(df_binary$own_2w))
cat("\n4W ownership (binary):\n")
print(table(df_binary$own_4w))
cat("\nPurpose group (binary):\n")
print(table(df_binary$purpose_group))
cat("\nTrips per week (binary):\n")
print(table(df_binary$trips_week_bin))
cat("\nOD distance (binary):\n")
print(table(df_binary$od_distance_bin))
cat("\nOD fare (binary):\n")
print(table(df_binary$od_fare_bin))
cat("\nOD time (binary):\n")
print(table(df_binary$od_time_bin))
cat("\nTotal rows used:", nrow(df_binary), "\n")
# ---- 4. Run the model ----
model_binary_only <- lm(
  access_egress ~ mode_group + age + gender + purpose_group +
    od_time_bin + od_fare_bin + od_distance_bin + trips_week_bin +
    own_2w + own_4w,
  data = df_binary
)
cat("\n============================================\n")
cat("Binary Mode Model (all predictors binary) | n =", nrow(df_binary), "\n")
cat("============================================\n")
print(summary(model_binary_only))
tidy_binary_only <- tidy(model_binary_only)




























# ============================================================
# Amritsar Survey — AFTER BUS DEPLOYMENT Model (with coefficients + significance stars)
#
# CORRECTED ASSUMPTION:
#   Bus access-egress distance = average access_egress computed ONLY
#   among the SHIFTED riders (not the whole survey population)
# ============================================================

# ---- 1. Packages ----
library(readxl)
library(dplyr)
library(broom)

# ---- 2. Load data ----
file_path <- "/Users/princek.patel/Desktop/CEEW/Work/UM- Amrtisar survey data analysis- 20Nov25.xlsx"
df_raw <- read_excel(
  file_path,
  sheet = "Cleaned Amritsar Main Data",
  skip = 1
)
cat("Rows loaded:", nrow(df_raw), " | Columns loaded:", ncol(df_raw), "\n")

# ---- 3. Build the same cleaned BEFORE dataset ----
df_binary <- df_raw %>%
  select(
    mode        = od_q_10,
    gender      = od_q_5,
    age         = od_q_6,
    own_2w_raw  = od_q_8_1_2W,
    own_4w_raw  = od_q_8_2_4W,
    purpose_raw = od_q_9,
    trips_week  = od_q_11,
    od_distance = od_q_14,
    od_time     = od_q_15,
    od_fare     = od_q_16,
    access_m    = od_q_18,
    egress_m    = od_q_21
  ) %>%
  mutate(
    age           = as.numeric(age),
    trips_week    = as.numeric(trips_week),
    od_distance   = as.numeric(od_distance),
    od_time       = as.numeric(od_time),
    od_fare       = as.numeric(od_fare),
    access_m      = as.numeric(access_m),
    egress_m      = as.numeric(egress_m),
    access_egress = access_m + egress_m,
    gender        = factor(gender),
    
    own_2w_raw    = as.numeric(own_2w_raw),
    own_4w_raw    = as.numeric(own_4w_raw),
    own_2w        = factor(if_else(own_2w_raw >= 1, "Yes", "No"), levels = c("No", "Yes")),
    own_4w        = factor(if_else(own_4w_raw >= 1, "Yes", "No"), levels = c("No", "Yes")),
    
    purpose_group = case_when(
      purpose_raw == "Work" ~ "Work",
      TRUE ~ "Other"
    ),
    purpose_group = factor(purpose_group, levels = c("Other", "Work")),
    
    trips_week_bin  = factor(if_else(trips_week >= 5, "High", "Low"), levels = c("Low", "High")),
    od_distance_bin = factor(if_else(od_distance <= 5, "Short", "Long"), levels = c("Long", "Short")),
    od_fare_bin     = factor(if_else(od_fare <= 10, "Low", "High"), levels = c("High", "Low")),
    od_time_bin     = factor(if_else(od_time <= 10, "Short", "Long"), levels = c("Long", "Short"))
  ) %>%
  filter(mode %in% c("Shared Autorickshaw", "Shared E-Rickshaw", "Two Wheeler")) %>%
  mutate(
    mode_group = case_when(
      mode %in% c("Shared Autorickshaw", "Shared E-Rickshaw") ~ "Rickshaw",
      mode == "Two Wheeler" ~ "Two Wheeler"
    ),
    mode_group = factor(mode_group, levels = c("Two Wheeler", "Rickshaw"))
  ) %>%
  filter(
    !is.na(access_egress), !is.na(mode_group),
    !is.na(gender), !is.na(age),
    !is.na(own_2w), !is.na(own_4w),
    !is.na(purpose_group),
    !is.na(trips_week_bin), !is.na(od_distance_bin),
    !is.na(od_time_bin), !is.na(od_fare_bin)
  )

cat("\nTotal rows used (BEFORE):", nrow(df_binary), "\n")

# ============================================================
# ---- 4. Fare slab lookup function (AFTER fare, per fare table) ----
# ============================================================
get_bus_fare <- function(distance_km) {
  case_when(
    distance_km <= 3                       ~ 5,
    distance_km > 3  & distance_km <= 6    ~ 10,
    distance_km > 6  & distance_km <= 10   ~ 15,
    distance_km > 10 & distance_km <= 15   ~ 20,
    distance_km > 15 & distance_km <= 20   ~ 25,
    distance_km > 20                       ~ 30,
    TRUE                                   ~ NA_real_
  )
}

# ============================================================
# ---- 5. Apply shift % per mode group (30% 2W, 50% Rickshaw) FIRST ----
# ============================================================
shift_pct_2w  <- 0.30
shift_pct_rik <- 0.50
set.seed(123)

df_shifted <- df_binary %>%
  group_by(mode_group) %>%
  mutate(
    shift_prob = if_else(mode_group == "Two Wheeler", shift_pct_2w, shift_pct_rik),
    shifted    = rbinom(n(), size = 1, prob = shift_prob)
  ) %>%
  ungroup()

cat("\nShifted vs Not shifted counts (by mode):\n")
print(table(df_shifted$mode_group, df_shifted$shifted))

# ============================================================
# ---- 6. CORRECTED: assumed bus access-egress = average ONLY
#         among the shifted riders (not the whole population) ----
# ============================================================
assumed_bus_access_egress <- df_shifted %>%
  filter(shifted == 1) %>%
  summarise(avg = mean(access_egress, na.rm = TRUE)) %>%
  pull(avg)

cat("\nAssumed bus access-egress distance (average of SHIFTED riders only, m):",
    round(assumed_bus_access_egress, 1), "\n")

# ============================================================
# ---- 7. Build AFTER dataset using this corrected assumption ----
# ============================================================
df_after_full <- df_shifted %>%
  mutate(
    mode_group_after = if_else(shifted == 1, "Bus", as.character(mode_group)),
    mode_group_after = factor(mode_group_after,
                              levels = c("Two Wheeler", "Rickshaw", "Bus")),
    
    access_egress_after = if_else(shifted == 1, assumed_bus_access_egress, access_egress),
    od_fare_after        = if_else(shifted == 1, get_bus_fare(od_distance), od_fare)
  )

cat("\nAFTER mode split (post-deployment):\n")
print(table(df_after_full$mode_group_after))

df_after_full <- df_after_full %>%
  mutate(
    od_fare_bin_after = factor(if_else(od_fare_after <= 10, "Low", "High"),
                               levels = c("High", "Low"))
  )

# ============================================================
# ---- 8. Run regression on AFTER dataset (3-level mode_group) ----
# ============================================================
model_after <- lm(
  access_egress_after ~ mode_group_after + age + gender + purpose_group +
    od_time_bin + od_fare_bin_after + od_distance_bin + trips_week_bin +
    own_2w + own_4w,
  data = df_after_full
)

cat("\n============================================\n")
cat("AFTER Bus Deployment Model | n =", nrow(df_after_full), "\n")
cat("============================================\n")
print(summary(model_after))

tidy_after <- tidy(model_after)

# ---- Add significance stars ----
tidy_after <- tidy_after %>%
  mutate(
    sig_stars = case_when(
      p.value < 0.01 ~ "***",
      p.value < 0.05 ~ "**",
      p.value < 0.10 ~ "*",
      TRUE           ~ ""
    ),
    estimate_display = paste0(round(estimate, 3), sig_stars)
  )

cat("\n===== AFTER Model Coefficient Table (with significance stars) =====\n")
print(tidy_after)
cat("\nSignificance codes: *** p<0.01  ** p<0.05  * p<0.1\n")

# ============================================================
# ---- 9. Before vs After comparison summary, by mode ----
# ============================================================
comparison_summary <- df_after_full %>%
  group_by(mode_group_after) %>%
  summarise(
    n                 = n(),
    avg_access_egress = mean(access_egress_after, na.rm = TRUE),
    avg_fare          = mean(od_fare_after, na.rm = TRUE)
  )

cat("\n===== AFTER Summary by Mode (incl. Bus) =====\n")
print(comparison_summary)