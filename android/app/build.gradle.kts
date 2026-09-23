plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "in.crimemap.locality"
    compileSdk = 35

    defaultConfig {
        applicationId = "in.crimemap.locality"
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "0.1"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            // Signing is configured by the person who builds for release,
            // in a local file that is never committed. See android/README.md.
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
}

// The app is the published dashboard, bundled. It is copied in from the
// pipeline's output at build time rather than kept in the repository, so
// the app can never show a page the pipeline did not build, and its
// freshness stamps are the pipeline's own.
val dashboard = rootProject.file("../site/locality.html")

val copyDashboard by tasks.registering(Copy::class) {
    doFirst {
        check(dashboard.exists()) {
            "No dashboard to bundle. Build it first from the repository root:\n" +
            "  PYTHONPATH=. python3 -m pipeline.mumbai && " +
            "PYTHONPATH=. python3 scripts/build_mumbai_stations.py && " +
            "PYTHONPATH=. python3 -m pipeline.build_locality_page"
        }
    }
    from(dashboard)
    into(layout.projectDirectory.dir("src/main/assets"))
    // The one change made to the page: its web-font links. The app has no
    // network permission to fetch them, so they are dropped and the page's
    // own system-font fallbacks apply. Everything else is byte for byte.
    filter { line ->
        if (line.contains("fonts.googleapis.com") || line.contains("fonts.gstatic.com")) "" else line
    }
}

tasks.named("preBuild") {
    dependsOn(copyDashboard)
}

dependencies {
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.appcompat:appcompat:1.7.0")
    implementation("androidx.activity:activity-ktx:1.9.3")
    implementation("androidx.webkit:webkit:1.12.1")
}
