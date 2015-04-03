'use strict';

angular.module('providerApp.version', [
  'providerApp.version.interpolate-filter',
  'providerApp.version.version-directive'
])

.value('version', '0.1');
