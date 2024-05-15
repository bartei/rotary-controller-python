# CHANGELOG



## v0.2.15-rc.3 (2024-05-14)

### Fix

* fix: revert latest version of kivy ([`1f9e6c0`](https://github.com/bartei/rotary-controller-python/commit/1f9e6c0203dac33ebc8ad72d083580732452f583))

### Unknown

* Merge remote-tracking branch &#39;origin/dev&#39; into dev ([`2784a63`](https://github.com/bartei/rotary-controller-python/commit/2784a6335f6081b9a0b76a3e4743bb3d4e198515))


## v0.2.15-rc.2 (2024-05-14)

### Fix

* fix: use kivy version 2.1.0 ([`9879560`](https://github.com/bartei/rotary-controller-python/commit/98795607f9a74dc764dd6bbb4d999669db8c515e))


## v0.2.15-rc.1 (2024-05-12)

### Fix

* fix: add pre-release workflow for dev branch ([`cedb688`](https://github.com/bartei/rotary-controller-python/commit/cedb688b452092d8d6ec242759442ed4911b9ff6))

* fix: add template service for systemd automated startup ([`7a768ca`](https://github.com/bartei/rotary-controller-python/commit/7a768cab236eefa095a0ac100d0d01a498bf0670))

* fix: update permissions ([`415289b`](https://github.com/bartei/rotary-controller-python/commit/415289bc49adc37db2891cc0691462c57a9f699d))

* fix: add start.sh script ([`29b0acf`](https://github.com/bartei/rotary-controller-python/commit/29b0acf9ee61bf4743d18072628a2a913fdeabc7))

* fix: cleanup imports ([`ad30596`](https://github.com/bartei/rotary-controller-python/commit/ad305961f81ed6a151c3ba28eab0af4bec14358e))

* fix: add form to configure circle pattern
fix: add rendering of circle pattern
fix: update grid look and feel
fix: rename scene_popup ([`ddc6189`](https://github.com/bartei/rotary-controller-python/commit/ddc618965c0ac22656ec86cbc2b5f03b5219d7a7))

* fix: several improvements to the code layout
fix: additions and toolbar for the plot view ([`5916a70`](https://github.com/bartei/rotary-controller-python/commit/5916a700910c87442ad499b9bd7c281f88b404dc))

* fix: wip on the gui for plot mode ([`d4daa67`](https://github.com/bartei/rotary-controller-python/commit/d4daa67dbda3b95c34029c68881be74523af9120))

* fix: revert save_id ([`bc1679e`](https://github.com/bartei/rotary-controller-python/commit/bc1679e4f98f25887f7b4bb2e6d30f2658426dc7))

* fix: improved rendering of the home page for small screens ([`cea9b11`](https://github.com/bartei/rotary-controller-python/commit/cea9b1173cf9c60b1253c3a2a489473b902bc690))

* fix: handle keyboard reference properly for systemanddock mode ([`4ce9310`](https://github.com/bartei/rotary-controller-python/commit/4ce931091b8aedc91d5f8ad69a86652be8adccfa))

* fix: bad default values configured for serial comm ([`6bd78a5`](https://github.com/bartei/rotary-controller-python/commit/6bd78a5e54bbddc18bed2b5fbbfc931a2883391f))

* fix: add back the fps indicator for the screen ([`c05d4ed`](https://github.com/bartei/rotary-controller-python/commit/c05d4edac54cde737c521c6d6554c3fd89757c47))

* fix: cleanup setup component
fix: update poetry
fix: improve main refresh loops ([`3285be0`](https://github.com/bartei/rotary-controller-python/commit/3285be0e141e75f758aab03a6f8ce165ce78ebf5))

* fix: rename variables from device to follow standard C notation
fix: handle enable signal manually from UI to prevent positioning glitches with some servo drives
fix: minor correction on the sizing of servo panel
fix: remove now deprecated addresses.py
fix: cleanup imports in base_device.py
fix: cleanup imports in communication.py
fix: move SCALES_COUNT in devices.py
fix: remove unmaintained tests ([`0a2c85b`](https://github.com/bartei/rotary-controller-python/commit/0a2c85bc28d64820aa64d933099654651791b0ba))

* fix: prevent undesired value updates to go to the device when starting the app
fix: add half function to the numeric keypad ([`ab58334`](https://github.com/bartei/rotary-controller-python/commit/ab58334567bcaac66ff513b1a937e9687767a8de))

* fix: new comm protocol tested ([`d0ff91a`](https://github.com/bartei/rotary-controller-python/commit/d0ff91aa46a98fe188c5a6ead3c5f673348f5317))

* fix: update servobar with new interface to device ([`a3111b5`](https://github.com/bartei/rotary-controller-python/commit/a3111b5afd0cdf713a35807dc979edf22befb1a3))

* fix: update references in coordbar for thew device interface ([`83e8e9a`](https://github.com/bartei/rotary-controller-python/commit/83e8e9aa1081d670f7b00ce69a62c3083bd6dc75))

* fix: cleaned up tuple for fast data ([`294a842`](https://github.com/bartei/rotary-controller-python/commit/294a842bda790df54c35bae096920d063be2deb8))

* fix: working array accessor mode for variable definitions ([`32278c8`](https://github.com/bartei/rotary-controller-python/commit/32278c87714a9ab0e57b3c83bc6588f2eadf767f))

* fix: working array accessor mode for variable definitions ([`4f6fd85`](https://github.com/bartei/rotary-controller-python/commit/4f6fd8596fd46d2acd3735a82b15a6cdd6a9d78b))

* fix: add fast data mode to be tested ([`7bd3046`](https://github.com/bartei/rotary-controller-python/commit/7bd3046f46756b476db533a281e8f7460b97cbe6))

* fix: driver working again with dict access mode ([`075b0ef`](https://github.com/bartei/rotary-controller-python/commit/075b0efeb595e6cdb01ed745965a1a9ba233758b))

* fix: broken comm ([`30e69a3`](https://github.com/bartei/rotary-controller-python/commit/30e69a3c8c48f9fa55b2bd07a68bd5c448692810))

* fix: add fastdata variable for interrupt period
fix: add placeholder for enable led ([`bb8546d`](https://github.com/bartei/rotary-controller-python/commit/bb8546d2599866c6a2fdb3502647c1c96a03a500))

* fix: new variables and new speed fastdata fields ([`146b149`](https://github.com/bartei/rotary-controller-python/commit/146b149079c880cb31a042c94baf08dce741d3a3))

* fix: set correct value when changing position in imperial mode
fix: check for value type to prevent int iteration when validating field value changes ([`b040229`](https://github.com/bartei/rotary-controller-python/commit/b040229cab0e07f1cb4d5366b593a33cb74fd65a))

* fix: set correct value when changing position in imperial mode
fix: check for value type to prevent int iteration when validating field value changes ([`36ff65b`](https://github.com/bartei/rotary-controller-python/commit/36ff65b203a24883be26862d2c9c8fd51f3fd3e7))

* fix: improvements to the homepage refresh rates ([`2473eb0`](https://github.com/bartei/rotary-controller-python/commit/2473eb0de8a703d8ee59d6c99526bc401a6835c7))

* fix: disable saving the sync_enable status in the settings file
fix: add manual update when exiting from the setup page
fix: add servospeed value from the fastdata
fix: add more logging to track what&#39;s being sent over to the modbus ([`233f565`](https://github.com/bartei/rotary-controller-python/commit/233f56554a404da390e45a21e3ef4d3c371e8f14))

* fix: coordbar disable when in sync mode
fix: ratio scaling not needed anymore for sync_ratio_den
fix: add back refresh for cycles and interval ([`8c5c557`](https://github.com/bartei/rotary-controller-python/commit/8c5c5578db2f89d0b887ec7181a12451013bb5f8))

### Unknown

* wip: update packages and add plot graphical items ([`0f92ec3`](https://github.com/bartei/rotary-controller-python/commit/0f92ec30727976bd2923ab450058e600ae9a01fa))

* Merge remote-tracking branch &#39;origin/dev&#39; into dev

# Conflicts:
#	rotary_controller_python/utils/base_device.py ([`da4ea0d`](https://github.com/bartei/rotary-controller-python/commit/da4ea0d6348d984fe3a081c4272e18d70579f060))

* Merge pull request #15 from thatch/keke-tracing

Add keke tracing to cwd/trace.out with ctrl-t ([`30b236a`](https://github.com/bartei/rotary-controller-python/commit/30b236a810135aa70920000e17434dbf1243392d))

* Add keke tracing to cwd/trace.out with ctrl-t ([`188c50b`](https://github.com/bartei/rotary-controller-python/commit/188c50b349ead17d5e171d3cbfa210d4505b541e))

* Merge branch &#39;spindle_mode&#39; into dev ([`b2d5d31`](https://github.com/bartei/rotary-controller-python/commit/b2d5d3153177a4c76354fb6e2dae34b664f3142f))


## v0.2.14 (2024-03-30)

### Fix

* fix: sync motion auto offsets working reliably
fix: remove some top bar refresh items to speed up the display
fix: add manual update command to app ([`97498b7`](https://github.com/bartei/rotary-controller-python/commit/97498b730b643391ba6c4064cf8ac2beb30935bc))

### Unknown

* Merge remote-tracking branch &#39;origin/main&#39; ([`914c375`](https://github.com/bartei/rotary-controller-python/commit/914c3758698c66c95728f160bc4719d894ad616a))


## v0.2.13 (2024-03-30)

### Fix

* fix: sync motion safety updates ([`7fb07cc`](https://github.com/bartei/rotary-controller-python/commit/7fb07cc7323eef36d213f9ac20fd22b48ba6c99c))

* fix: speedup speed bar refresh rate ([`9b43e0d`](https://github.com/bartei/rotary-controller-python/commit/9b43e0d1aa1982724fb30d1162aa38748d019160))

* fix: scale speed to proper normalized value ([`0f68409`](https://github.com/bartei/rotary-controller-python/commit/0f68409e2cf03edbc6b2ee3c3608960ffe578f41))

* fix: scale speed to proper normalized value ([`ecc4a77`](https://github.com/bartei/rotary-controller-python/commit/ecc4a7748882ad85bc7f5ddbe0f795600e82f3af))

* fix: remove info logs and update the speed bar value with estimated speed ([`950c094`](https://github.com/bartei/rotary-controller-python/commit/950c09407c294e7a1d8e93387a355d3beede9779))

* fix: testing ([`c6ec6e0`](https://github.com/bartei/rotary-controller-python/commit/c6ec6e02c7207c3ae8191427bdbaed9e67e8abaa))

### Unknown

* Merge remote-tracking branch &#39;origin/main&#39; ([`c1e7f18`](https://github.com/bartei/rotary-controller-python/commit/c1e7f184e593c1c13c95ceb0deff76678277e96a))

* debug: add max speed to status bar ([`d12f810`](https://github.com/bartei/rotary-controller-python/commit/d12f8107ec3ce2888d64f79541c2a8f5978c5d42))

* add logging info ([`35446a0`](https://github.com/bartei/rotary-controller-python/commit/35446a0359a144ea1d41fa2b3e0a29bec6a54261))

* add logging info ([`11137e1`](https://github.com/bartei/rotary-controller-python/commit/11137e13564ad6a80190b7be9a14742a38cff9c2))


## v0.2.12 (2024-03-28)

### Fix

* fix: error scaling of the speed bar ([`9bbcc06`](https://github.com/bartei/rotary-controller-python/commit/9bbcc065d98e096d48d491c4a5bf4238a217e449))

### Unknown

* Merge remote-tracking branch &#39;origin/main&#39; ([`784ab6b`](https://github.com/bartei/rotary-controller-python/commit/784ab6b89085c0321b2660cb9a39e0b5c8d636ab))


## v0.2.11 (2024-03-28)

### Fix

* fix: error scaling of the speed bar ([`90ba444`](https://github.com/bartei/rotary-controller-python/commit/90ba444affa8b0eeccae5dd3ae6be869720efcdf))

### Unknown

* Merge remote-tracking branch &#39;origin/main&#39; ([`b09598c`](https://github.com/bartei/rotary-controller-python/commit/b09598c97c0021d4c9b7594f5c42834f0e2ebb53))


## v0.2.10 (2024-03-28)

### Fix

* fix: error with type definition for servo steps ([`1cb47e6`](https://github.com/bartei/rotary-controller-python/commit/1cb47e65a33e65000e6e53c4c2ce6a4ad4cf6b89))

### Unknown

* Merge remote-tracking branch &#39;origin/main&#39; ([`f383e4c`](https://github.com/bartei/rotary-controller-python/commit/f383e4caab2fc6813eb6bf5ae990ed0a23819469))


## v0.2.9 (2024-03-28)

### Fix

* fix: checks for slow update ([`9b4769f`](https://github.com/bartei/rotary-controller-python/commit/9b4769f6b943b4ac2cb9531d806afcbd0bf6aa25))

### Unknown

* Merge remote-tracking branch &#39;origin/main&#39; ([`20cfc79`](https://github.com/bartei/rotary-controller-python/commit/20cfc795d08060c4a4d8277f77fc15a1fd4d33ce))


## v0.2.8 (2024-03-28)

### Fix

* fix: update data source for the servo speed ([`20cb754`](https://github.com/bartei/rotary-controller-python/commit/20cb7546da4e032d45d5fa91f329cf5e088e9308))


## v0.2.7 (2024-03-28)

### Fix

* fix: add speed progress bar to indicate how far you are form the maximum allowed speed
fix: add second refresh routine that goes slower for top bar statuses ([`930635e`](https://github.com/bartei/rotary-controller-python/commit/930635ebd936287bbc42f53f03be1f9f0441ed82))

### Unknown

* Merge remote-tracking branch &#39;origin/main&#39; ([`04f4f61`](https://github.com/bartei/rotary-controller-python/commit/04f4f611508eecd68d6ea4a5873e45c990983374))


## v0.2.6 (2024-03-21)

### Fix

* fix: configure variable type for serial port and serial baudrate properties ([`f737866`](https://github.com/bartei/rotary-controller-python/commit/f73786615bcddc55854db04db15e1f5ce55fb646))


## v0.2.5 (2024-03-16)

### Fix

* fix: add address and baudrate in config.ini ([`957c5a9`](https://github.com/bartei/rotary-controller-python/commit/957c5a9426bcee8ad4e9f0526b00dd1cb70762d4))

### Unknown

* Merge remote-tracking branch &#39;origin/main&#39; ([`ddb3e34`](https://github.com/bartei/rotary-controller-python/commit/ddb3e346ec7669bd9b6ae7bc8570a7419f5d84c0))


## v0.2.4 (2024-03-16)

### Fix

* fix: remove unused file
fix: better default values for scales ([`6ef54ab`](https://github.com/bartei/rotary-controller-python/commit/6ef54abcd00aab26eb462e20fd8e4de9f4f435e8))

### Unknown

* Merge remote-tracking branch &#39;origin/main&#39; ([`3329e65`](https://github.com/bartei/rotary-controller-python/commit/3329e655c151a7fe487a1fdca73185d22378e299))


## v0.2.3 (2024-03-16)

### Fix

* fix: improvements to the setup dialog ([`886bcb5`](https://github.com/bartei/rotary-controller-python/commit/886bcb51b8ac988de25bc49ec20f5b106efd091d))

* fix: add keyboard bindings for the keypad dialog ([`bb04bae`](https://github.com/bartei/rotary-controller-python/commit/bb04bae0bb0cb200cae41824edc3750ce7709c26))


## v0.2.2 (2024-03-16)

### Fix

* fix: add link for help dialog to the setup page
fix: add rst text for the scales ([`11095c1`](https://github.com/bartei/rotary-controller-python/commit/11095c19a38a086544adf0a43bc1f31ecda70765))

* fix: handle int or float type for keypad confirm ([`20233d1`](https://github.com/bartei/rotary-controller-python/commit/20233d1f1e2e66607c8e56941280aa6f30215b79))

### Unknown

* Merge remote-tracking branch &#39;origin/main&#39; ([`d8a1199`](https://github.com/bartei/rotary-controller-python/commit/d8a1199e688d21a8a8eac672a049d52c8644132f))


## v0.2.1 (2024-03-16)

### Fix

* fix: check value for confirmation from keypad ([`85333ac`](https://github.com/bartei/rotary-controller-python/commit/85333ac65a71112dd67d7945f1a39f5bf2797b7f))

### Unknown

* Merge remote-tracking branch &#39;origin/main&#39; ([`cdd275c`](https://github.com/bartei/rotary-controller-python/commit/cdd275cc7b0cb17a0c55b3f61ee0c71dee05ec2f))


## v0.2.0 (2024-03-13)

### Feature

* feat: update logging for keypad ([`14fb684`](https://github.com/bartei/rotary-controller-python/commit/14fb684e80b1bd0cbea5181c6584a6ddc3b181a6))

* feat: update to latest Kivy version ([`3d0ee4d`](https://github.com/bartei/rotary-controller-python/commit/3d0ee4d8223b110d9670a7a510333b52b15d0e9b))

### Fix

* fix: version_toml for semantic release ([`c5161c5`](https://github.com/bartei/rotary-controller-python/commit/c5161c5857d92598e0a42638f1d34e89c19e9c36))

* fix: update packages and clenaup logging
fix: update .gitignore ([`9080334`](https://github.com/bartei/rotary-controller-python/commit/908033412f51390e3eb5ef1c9615a3e32e055f5d))

* fix: clenaup toolbar ([`b7aee39`](https://github.com/bartei/rotary-controller-python/commit/b7aee3996fafe138040af367de7ce5e2aadcf0d6))

* fix: update loging for synchro ([`4ab6a0d`](https://github.com/bartei/rotary-controller-python/commit/4ab6a0dda884c9a70ef7682d71c8db61d41aa7b8))

* fix: update logging for statusbar ([`193e05e`](https://github.com/bartei/rotary-controller-python/commit/193e05e10265c1f573203868e3114453fbd6940d))

* fix: add logs panel in the settings dialog ([`1ac306a`](https://github.com/bartei/rotary-controller-python/commit/1ac306a4cf819d13ed89993f71018bba66b8d564))

* fix: update logging for servobar ([`a47df92`](https://github.com/bartei/rotary-controller-python/commit/a47df92696cab1a49552da5dacce7a53184bff05))

* fix: minor improvements in rendering of servobar ([`2fde7d1`](https://github.com/bartei/rotary-controller-python/commit/2fde7d19948b42a4c54237ccba19712b43111862))

* fix: update logging for ledbutton ([`106129d`](https://github.com/bartei/rotary-controller-python/commit/106129db5c3910d6a154f5260b4ca1f05430a7fd))

* fix: update logging for labelbutton ([`e8ac9d3`](https://github.com/bartei/rotary-controller-python/commit/e8ac9d37ebce175df86c8a479e95f65f8aee33aa))

* fix: update logging for coordbar ([`8151069`](https://github.com/bartei/rotary-controller-python/commit/8151069c429d6f31b2b75e6d40ed98e27d12d5dd))

* fix: support various screen sizes for coordbar ([`640efcb`](https://github.com/bartei/rotary-controller-python/commit/640efcb187f74b7bca80dd663834014f426fac49))

* fix: remove unnecessary load of kv file for AppSettings ([`8136347`](https://github.com/bartei/rotary-controller-python/commit/813634797b22b65fa80926a34183bca2b6c61f26))

* fix: try fast comm speed ([`ca3c60e`](https://github.com/bartei/rotary-controller-python/commit/ca3c60ea6ba1fc75559318a5c465c6dea3675de6))

* fix: try fast comm speed ([`76df77f`](https://github.com/bartei/rotary-controller-python/commit/76df77f38ff47951b759c088cf3cb6c17b97f392))

* fix: remove wrong scaling for scale ratios ([`bb6be99`](https://github.com/bartei/rotary-controller-python/commit/bb6be995eb1e27f5e60d095c894e1da3338bfdfe))

* fix: remove high speed execution interval
fix: add event to update ratio num and ratio den for scales
fix: rename panels ([`b92743b`](https://github.com/bartei/rotary-controller-python/commit/b92743b80af3c7e75a7963500d6b3e80affb433b))

* fix: add log message for written longs ([`ed2d4c8`](https://github.com/bartei/rotary-controller-python/commit/ed2d4c8d1f50028b30af7356bad1c2222ad219da))

* fix: scaling of ratio den write
fix refresh interval ([`46ba430`](https://github.com/bartei/rotary-controller-python/commit/46ba4300285b7fb8c12270e0162b337d6abca47e))

* fix: minor ui improvements ([`b580043`](https://github.com/bartei/rotary-controller-python/commit/b58004334f519d4dd18706a29ebc02883e1cd510))

* fix: add speed indication ([`a911114`](https://github.com/bartei/rotary-controller-python/commit/a91111448a33598758e32d3fd108ac494298713f))

* fix: normalize syn ratio den for scales ([`7c9cd13`](https://github.com/bartei/rotary-controller-python/commit/7c9cd13f8a086ca3f95af406e679348afe55094c))

* fix: normalize syn ratio den for scales ([`785aa9c`](https://github.com/bartei/rotary-controller-python/commit/785aa9c2ccabda391922f6e9174c0adc2244ac65))

* fix: normalize syn ratio den for scales ([`c53ae5f`](https://github.com/bartei/rotary-controller-python/commit/c53ae5fff95872d8706ab0321b31e6dd863508eb))

* fix: normalize syn ratio den for scales ([`a0a63e3`](https://github.com/bartei/rotary-controller-python/commit/a0a63e3d64f0f59ba040dea8eaa7803bab6f5986))

* fix: reduce speed to 57600 ([`5dcbd9a`](https://github.com/bartei/rotary-controller-python/commit/5dcbd9a50bd2c3868e1481a433bff6523f4de841))

* fix: fast mode ([`ef06f46`](https://github.com/bartei/rotary-controller-python/commit/ef06f46c758aaa4f5a757729cfac98abd045def7))

* fix: fast mode ([`1fa4730`](https://github.com/bartei/rotary-controller-python/commit/1fa4730f5af07b547741f1f3a163a14d1c197adf))

* fix: test ([`82dec11`](https://github.com/bartei/rotary-controller-python/commit/82dec11cbd26dfde4cb6623a988dfef4c749c905))

* fix: test ([`8641ebf`](https://github.com/bartei/rotary-controller-python/commit/8641ebf31202639657b48d3cc029968d0c4dd514))

* fix: test ([`9ef8c2d`](https://github.com/bartei/rotary-controller-python/commit/9ef8c2d7ffb2cefd43d770981099fb3085a43b3e))

* fix: speed improvements, and metrics ([`c83f7b5`](https://github.com/bartei/rotary-controller-python/commit/c83f7b5961a5f6edb9d4702756ddb958acc274c4))

* fix: formatting ([`938c4c7`](https://github.com/bartei/rotary-controller-python/commit/938c4c792990f1becab457d5acc79814d3456c3d))

* fix: new improved version ([`7ce7d6c`](https://github.com/bartei/rotary-controller-python/commit/7ce7d6c76b5292d20be950dc429e3eef4b798801))

* fix: updates to the whole project ([`5ce73c9`](https://github.com/bartei/rotary-controller-python/commit/5ce73c9122e5aa1d8f784794d4e9dfec1568f3ea))

* fix: updates for new c code ([`6d475e0`](https://github.com/bartei/rotary-controller-python/commit/6d475e064e464279632ba6da96a02858cf5dea61))

* fix: communication speed ([`8e510a3`](https://github.com/bartei/rotary-controller-python/commit/8e510a3b3daa52f88879e52207d78fe77d0a8795))

* fix: add button to configure networking ([`c4541cc`](https://github.com/bartei/rotary-controller-python/commit/c4541cc89aaf2a731e9f5e00b8effe84c1b894a6))

* fix: remove pyyaml
fix: remove secondary kivy repo ([`3b1e643`](https://github.com/bartei/rotary-controller-python/commit/3b1e643fe0b6ba630221bccf0768b0f5f44d103d))

* fix: update deps
fix: add wip for interfaces configuration ([`07ed51d`](https://github.com/bartei/rotary-controller-python/commit/07ed51dd4d2cd55bf78491fdab0dca454188e314))


## v0.1.6 (2023-06-22)

### Fix

* fix: enable pypi ([`ba42a6e`](https://github.com/bartei/rotary-controller-python/commit/ba42a6ecbd3b78d44668095100eb7c3cd1872649))

### Unknown

* Merge remote-tracking branch &#39;origin/main&#39; ([`d99bfd0`](https://github.com/bartei/rotary-controller-python/commit/d99bfd0cb1756a46e9760fc448743ff315777447))

* Merge branch &#39;config&#39; ([`e114d76`](https://github.com/bartei/rotary-controller-python/commit/e114d76318234a2a6aa3cc914dc520e35be4fdca))


## v0.1.5 (2023-06-22)

### Fix

* fix: update packages and release ([`e9d7b56`](https://github.com/bartei/rotary-controller-python/commit/e9d7b56c592256cdbf565530c1a431b161146e20))

* fix: log handling with loguru ([`4239c7c`](https://github.com/bartei/rotary-controller-python/commit/4239c7cd76042e94aae7d8445a3f04d47d82b9f6))

* fix: proper config handling for servo and axis bars ([`d7a5141`](https://github.com/bartei/rotary-controller-python/commit/d7a5141a788fbb59fc7abc8e1b308a5c4b558fa7))

* fix: wip synchro ([`5de6dd7`](https://github.com/bartei/rotary-controller-python/commit/5de6dd793363515aba16d03612af5f2b6460406c))

### Unknown

* Merge remote-tracking branch &#39;origin/main&#39; ([`1bd3e8b`](https://github.com/bartei/rotary-controller-python/commit/1bd3e8b6ba242beabeabc6c9a3f6f7e43476c10b))

* Merge pull request #1 from bartei/bartei-patch-1

Create main.yml ([`c16f455`](https://github.com/bartei/rotary-controller-python/commit/c16f4556abb341f7fd6859cea3f07969ed6ee6f3))

* Create main.yml ([`c8d0aff`](https://github.com/bartei/rotary-controller-python/commit/c8d0aff5d4b76baf02334dbd6442befe574eddb3))

* Merge branch &#39;old&#39; ([`9bccf04`](https://github.com/bartei/rotary-controller-python/commit/9bccf04459d265611e15e65dfe05a614dc345eb4))


## v0.1.4 (2023-04-03)

### Unknown

* Merge branch &#39;old&#39; into &#39;main&#39;

Minor fixes for reverted operation mode

See merge request sbertelli/rotary-controller-python!1 ([`b1f5d89`](https://github.com/bartei/rotary-controller-python/commit/b1f5d893e4e3ca6df99b6e625325c999241a580b))

* Minor fixes for reverted operation mode ([`01d0363`](https://github.com/bartei/rotary-controller-python/commit/01d03630a7afb6ee26aa67b429f30d8e9f995f52))


## v0.1.3 (2023-03-29)

### Fix

* fix: speed ([`980243a`](https://github.com/bartei/rotary-controller-python/commit/980243ad806a29a289f62f239ae81998c12010f0))


## v0.1.2 (2023-03-23)

### Fix

* fix: add missing code and update module refs ([`d2cd9cc`](https://github.com/bartei/rotary-controller-python/commit/d2cd9cc0ff4056a34abc9e94a4d911db8fd06328))

* fix: update gitignore ([`916d840`](https://github.com/bartei/rotary-controller-python/commit/916d840042e874c5bad26f35c066ef574e81290e))


## v0.1.1 (2023-03-21)

### Fix

* fix: restructure app to be a proper package module ([`1cff346`](https://github.com/bartei/rotary-controller-python/commit/1cff34637cc011be19afa0102fcd65c5b4190dbe))

### Unknown

* Merge remote-tracking branch &#39;origin/main&#39; ([`37435ad`](https://github.com/bartei/rotary-controller-python/commit/37435ad35d0efccf94d6414541031225de499e89))


## v0.1.0 (2023-03-21)

### Feature

* feat: use poetry
fix: add semantic config to pyproject.toml ([`b714f2b`](https://github.com/bartei/rotary-controller-python/commit/b714f2b33a163b1b577932af25c7fb0b49fea93d))

* feat: use poetry
fix: add pipeline for cicd ([`6ae38b0`](https://github.com/bartei/rotary-controller-python/commit/6ae38b0ccdf9e491b8d439205e8ca70b5dbcb73a))

* feat: new servo bar beta version
fix: colors
fix: defaults
fix: cleanup of unused stuff ([`4a23d0f`](https://github.com/bartei/rotary-controller-python/commit/4a23d0f9440f4f709eb5753ebec8898129c5c148))

* feat: proper handling of mode value ([`458d866`](https://github.com/bartei/rotary-controller-python/commit/458d8664507834eb1064d35ac69f2eac72b2d342))

* feat: add tabs for modes ([`01cb990`](https://github.com/bartei/rotary-controller-python/commit/01cb9904f9b2da3cb060c68a16f8043e94f81509))

* feat: initial test code ([`1a76b3c`](https://github.com/bartei/rotary-controller-python/commit/1a76b3cc8890e61ff59cddb8df7337c5685f8cd7))

* feat: add gitignore ([`81a3466`](https://github.com/bartei/rotary-controller-python/commit/81a346608aa9e5cb6d99e69768312900feb1ccad))

### Fix

* fix: test push ([`b0a5528`](https://github.com/bartei/rotary-controller-python/commit/b0a552899c448bd14ffd2d353afa5e677ee4019a))

* fix: numerous improvements ([`005e5c4`](https://github.com/bartei/rotary-controller-python/commit/005e5c45bfe928042301a4e9017ccd483fe478a2))

* fix: value updates ([`82cf146`](https://github.com/bartei/rotary-controller-python/commit/82cf1465b7b1def824c0e5febffd8809b7e0bdd5))

* fix: improvements and updates ([`41781e1`](https://github.com/bartei/rotary-controller-python/commit/41781e132ef3187db39678f75b170c8e07c8137a))

* fix: update screen layout to include n/d values for each axis
feat: add Iosevka font for numeric visualizations ([`1111efd`](https://github.com/bartei/rotary-controller-python/commit/1111efd2f5a6a678b9bc6dc0aa7ce66538f9b93c))

* fix: proper set coordinate conversion factors configured for X, Y and Z retrieved from the configuration values ([`6e8c1d4`](https://github.com/bartei/rotary-controller-python/commit/6e8c1d4de2b3ab3655cc305014250d51d26b9a17))

* fix: zero method for axis button ([`0ac3e4e`](https://github.com/bartei/rotary-controller-python/commit/0ac3e4eb35350c81cd3ab14b3c2b00fe8072d5ea))

* fix: improve read scales performance ([`050f3ce`](https://github.com/bartei/rotary-controller-python/commit/050f3cec19c88549648eb9ffed45a4eae03c7583))

* fix: add num den value for each input ([`92dda8c`](https://github.com/bartei/rotary-controller-python/commit/92dda8c31d901912a9ce37c5357667f325b9b15d))

* fix: gitignore ([`d902945`](https://github.com/bartei/rotary-controller-python/commit/d902945762abe633604b86cd0b470ac3dd081031))

* fix: improvements and updates ([`92b34f1`](https://github.com/bartei/rotary-controller-python/commit/92b34f13791a1c55d7580fa76fd3b05c3850f887))

* fix: add num/den for input encoder ([`243e148`](https://github.com/bartei/rotary-controller-python/commit/243e148140d870560d61dbef532c4a92bb12c7f7))

* fix: display properties and settings ([`b07d745`](https://github.com/bartei/rotary-controller-python/commit/b07d7455b6e6ea4fd6e7a33017f9e7c64c553907))

* fix: configure available modes ([`adfce2e`](https://github.com/bartei/rotary-controller-python/commit/adfce2ec37786ad4cd5fe824d3f2f28c3d1aff89))

* fix: update communication driver, no more bitfields
fix: add error and status to communication ([`b39fe8a`](https://github.com/bartei/rotary-controller-python/commit/b39fe8ac77c6e93b69ea95080dac2362d7cfe363))

* fix: numerous improvements to the UI ([`2172bca`](https://github.com/bartei/rotary-controller-python/commit/2172bcad830c3ff8841f566b1e983c55b29001e4))

* fix: added blinky and some more status indicators
fix: better layout and icons here and there ([`50bda0f`](https://github.com/bartei/rotary-controller-python/commit/50bda0f5bc13348c38b698439163ceaf20afe985))

* fix: testing status leds ([`7de5ebf`](https://github.com/bartei/rotary-controller-python/commit/7de5ebf36356360d50acb0f78c0505d7367a70b4))

* fix: return 0 on error for bitfields ([`f30737e`](https://github.com/bartei/rotary-controller-python/commit/f30737e2bc9920aa62f9a1a64cb3f41000961952))

* fix: add modules for bitfields and structures ([`4387217`](https://github.com/bartei/rotary-controller-python/commit/4387217bead6faa85fdf2d226bdf09c475565290))

* fix: update code from main
feat: add basic tab for sync mode
fix: move out the labelbutton into its own module
fix: rename components for tabs
fix: handle absent device at startup and in code ([`f4177d5`](https://github.com/bartei/rotary-controller-python/commit/f4177d557b4e31ad8049a31de7ad8d9973d72c3b))

* fix: further implementation of the status and control bits
feat: use caching for the bitfields ([`2bb2a52`](https://github.com/bartei/rotary-controller-python/commit/2bb2a52326b60f48ccbbd89be677e7b0167ff9ca))

* fix: add gitignore and exclusions
Tested-by: Stefano Bertelli &lt;bartei81@gmail.com&gt; ([`ff623d4`](https://github.com/bartei/rotary-controller-python/commit/ff623d48de65976a5773686249a478af37004c3d))

* fix: improve destination update checks and configs ([`a011b20`](https://github.com/bartei/rotary-controller-python/commit/a011b20cd6aecfcc0aa38a14860460a5ee5ec86b))

* fix: add rotary settings
fix: allow to go over full circle for now
fix: add json for rotary settings
fix: update communications
fix: add config values
fix: add properties to app ([`84f5db9`](https://github.com/bartei/rotary-controller-python/commit/84f5db944ac7db029527faa095bb2c3e66449ad5))

* fix: issues with the inputs and the keypad ([`cc38e36`](https://github.com/bartei/rotary-controller-python/commit/cc38e365e9511322cb829194153cd258f7b390db))

* fix: testing communication and other ui stuff ([`d2a294b`](https://github.com/bartei/rotary-controller-python/commit/d2a294b02d5ad344de4c6de28d904c3c0a0ee68a))

* fix: add communication library in utils ([`6c75f4a`](https://github.com/bartei/rotary-controller-python/commit/6c75f4ac761e2bbda28b0c557a3381e2c379dc7a))

* fix: add communication library in utils ([`0f30cf5`](https://github.com/bartei/rotary-controller-python/commit/0f30cf5f42332fa452697c1c3b861a44ae4d337f))

### Unknown

* rename config.ini to config.ini.factory ([`76472df`](https://github.com/bartei/rotary-controller-python/commit/76472dfa13480f280b7e8518c88ceb18106bc1a5))

* testing stuff ([`3489a8b`](https://github.com/bartei/rotary-controller-python/commit/3489a8b5566d48fd7890ef35b6a38c68e579c5fe))

* Merge branch &#39;main&#39; into tabs

# Conflicts:
#	components/rotarybar.kv
#	components/toolbar.kv
#	main.py ([`3663aab`](https://github.com/bartei/rotary-controller-python/commit/3663aab70f1bc4a19422a03b2ad6f0c5a52e8f35))

* fix communication ([`a6666ec`](https://github.com/bartei/rotary-controller-python/commit/a6666ecb7a6802c55bdb49cb200147fbc12f3d0d))

* many updates ([`16d9792`](https://github.com/bartei/rotary-controller-python/commit/16d97928c7d23430defa443e9cba3de4b7f5918a))

* Initial commit ([`f256af7`](https://github.com/bartei/rotary-controller-python/commit/f256af727a14503afb5ac31d8eb46221873ef644))
