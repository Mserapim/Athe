var scopes = {};

Object.defineProperty(scopes, 'READ', {
    enumerable: true,
    get: function () { return 1 }
});

Object.defineProperty(scopes, 'ADMIN', {
    enumerable: true,
    get: function () { return 2 }
});

Ext.ns('judicial.reminder');

Object.defineProperty(judicial.reminder, 'ScopeTypes', {
    enumerable: true,
    get: function() { return scopes }
});
