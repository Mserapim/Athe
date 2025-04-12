Ext._define('web.intranet.icons.Restful', {
  extend: 'core.Restful',

  resource: 'IntranetIconsRestful',

  getFields: function () {
    if (!this._fields)
      this._fields = web.intranet.icons.Restful.superclass.getFields.call(this).concat([
        { name: 'icons', type: 'auto' },
        { name: 'icon', type: 'string' },
        { name: 'title', type: 'string' },
        // { name: 'controller', type: 'string' },
        { name: 'application', type: 'int' },
        { name: 'application_unicode', type: 'string' },
        { name: 'application_active', type: 'bool' },
        { name: 'active', type: 'bool' },
        // { name: 'module', type: 'string' },
        { name: 'icon_file', type: 'int', useNull: true },
        { name: 'icon_file_unicode', type: 'string' },
        { name: 'position', type: 'int' }
      ]);

    return this._fields;
  }
});
