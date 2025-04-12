Ext._define('web.intranet.icons.Window', {
  extend: 'core.RestfulWindow',

  rest: 'web.intranet.icons.Restful',

  width: 360,

  getFormPanel: function (cfg) {
    if (!this._formPanel)
      this._formPanel = Ext._create('Ext.form.FormPanel', {
        border: false,
        frame: true,
        items: [
          this.getIcon(),
          {
            xtype: "checkbox",
            boxLabel: "Ativo?",
            fieldLabel: "",
            allowBlank: true,
            name: "active",
            width: 350
          },
          {
            xtype: 'textfield',
            fieldLabel: 'Posição',
            name: 'position',
            emptyText: '9999'
          },
        ]
      });

    return this._formPanel;
  },


  getIcon: function () {
    if (!this._getIcon) {
      this._getIcon = Ext._create('core.fields.FileUploadField', {
        hideLabel: true,
        name: 'icon_file',
        hideInputDisplay: true,
        width: 200,
        height: 200,
        listeners: {
          scope: this,
          afterchange: function (field, instance) {
            var path = [
              core.callAction(
                'FileUploadController',
                'get_image_file',
                instance.file_hash
              ),
              '1000.1000'
            ].join('');

            var style = 'url(' + path + ') no-repeat center center';
            field.ownerCt.body.dom.style.background = style;
            field.ownerCt.body.dom.style.backgroundSize = '150px';
          }
        }
      });
    }

    return this._getIcon;
  },


  constructor: function (cfg) {
    cfg = (cfg || {});

    Ext.applyIf(
      cfg,
      {}
    );
    web.intranet.icons.Window.superclass.constructor.call(this, cfg);
  }
});

