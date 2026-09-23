package `in`.crimemap.locality

import android.content.ActivityNotFoundException
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.activity.addCallback
import androidx.appcompat.app.AppCompatActivity
import androidx.webkit.WebSettingsCompat
import androidx.webkit.WebViewAssetLoader
import androidx.webkit.WebViewFeature

/**
 * The dashboard, bundled and shown offline.
 *
 * The page is served from the app's own assets under an https origin
 * (appassets.androidplatform.net) rather than a file:// URL, so that the
 * page's per-viewer conveniences in localStorage work and so that no
 * file access has to be switched on in the WebView at all.
 *
 * Two kinds of link leave the page, and both leave the app: a station's
 * phone number goes to the dialler, and a link to a station's own page on
 * mumbaipolice.gov.in goes to the browser. Nothing else is allowed to
 * navigate; the app has no INTERNET permission to load it with anyway.
 */
class MainActivity : AppCompatActivity() {

    private lateinit var web: WebView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        web = WebView(this)
        setContentView(web)

        val assets = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()

        with(web.settings) {
            javaScriptEnabled = true          // the map, search and panel are scripted
            domStorageEnabled = true          // localStorage: remembered search, nothing more
            allowFileAccess = false
            allowContentAccess = false
            setSupportZoom(true)
            builtInZoomControls = true
            displayZoomControls = false
            useWideViewPort = true
            loadWithOverviewMode = true
        }
        // The page styles itself for dark mode; this lets the WebView pass
        // the system setting through to its prefers-color-scheme query.
        if (WebViewFeature.isFeatureSupported(WebViewFeature.ALGORITHMIC_DARKENING)) {
            WebSettingsCompat.setAlgorithmicDarkeningAllowed(web.settings, true)
        }

        web.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(
                view: WebView, request: WebResourceRequest
            ): WebResourceResponse? = assets.shouldInterceptRequest(request.url)

            override fun shouldOverrideUrlLoading(
                view: WebView, request: WebResourceRequest
            ): Boolean {
                val url = request.url
                return when {
                    url.host == "appassets.androidplatform.net" -> false
                    url.scheme == "tel" -> { handOff(Intent(Intent.ACTION_DIAL, url)); true }
                    url.scheme == "http" || url.scheme == "https" ->
                        { handOff(Intent(Intent.ACTION_VIEW, url)); true }
                    else -> true
                }
            }
        }

        onBackPressedDispatcher.addCallback(this) {
            if (web.canGoBack()) web.goBack() else finish()
        }

        if (savedInstanceState == null) {
            web.loadUrl(DASHBOARD)
        } else {
            web.restoreState(savedInstanceState)
        }
    }

    private fun handOff(intent: Intent) {
        try {
            startActivity(intent)
        } catch (e: ActivityNotFoundException) {
            Toast.makeText(this, R.string.no_app_for_link, Toast.LENGTH_SHORT).show()
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        web.saveState(outState)
    }

    override fun onDestroy() {
        web.destroy()
        super.onDestroy()
    }

    private companion object {
        const val DASHBOARD = "https://appassets.androidplatform.net/assets/locality.html"
    }
}
