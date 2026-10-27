# Windows MongoDB startup correction — 24 October 2026

The Windows screenshot shows MongoMemoryServer exiting with code 2; STN then reports ECONNREFUSED on 127.0.0.1:27017. The local Mongo launcher incorrectly passed --nounixsocket on Windows, although MongoDB supports that option only on Unix-based systems.

Fixed integration/mongo_local.mjs:
- Windows omits --nounixsocket; Linux/macOS retain it.
- MongoDB stays on fixed loopback port 27017. It cannot silently choose a different port while STN still uses 27017.
- Persistent local data stays at integration-data/mongo; existing CN logins/data are untouched.
- Startup failures are saved at integration-data/mongo-startup.log.

Install the small patch:
1. Close the MongoDB and combined-app command windows.
2. Extract STN_CN_Windows_Mongo_Fix.zip. Copy its integration folder into your existing STN_CN_Integration_Local folder. Choose Replace for integration/mongo_local.mjs.
3. Run Start_Local_Mongo_Windows.bat. Wait for 'MongoDB ready on 127.0.0.1:27017' and leave that window open.
4. Run Start_Combined_Windows.bat and open http://127.0.0.1:8787/portal. Use your existing login.

No npm reinstall, account setup or data deletion is required for this patch.
If MongoDB still fails, share integration-data/mongo-startup.log.

Verification: three platform-argument checks passed, including simulated Windows argument construction. Actual MongoDB persistent restart on Linux retained saved data and worked in a path containing spaces. The prior combined-application results remain in the main package; this patch adds the targeted platform and MongoDB restart checks. Actual Windows execution/acceptance must be retested on your PC.

Official reference: https://www.mongodb.com/docs/v8.0/reference/program/mongod/ (--nounixsocket applies only to Unix-based systems).
