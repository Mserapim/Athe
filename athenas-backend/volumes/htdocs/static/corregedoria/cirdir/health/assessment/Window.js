Ext._define('corregedoria.cirdir.health.assessment.Window', {
    extend: 'core.RestfulWindow',

    rest: 'corregedoria.cirdir.health.assessment.Restful',

    width: 800,

    getEmployeeField: function() {
      if(!this._employeeField) {
          this._employeeField = Ext._create('core.fields.AutocompleteField', {
              xtype: "rest-autocompletefield",
              fieldLabel: 'Avaliador',
              allowBlank: true,
              rest: "corregedoria.cirdir.EmployeeRestful",
              name: "employee",
              disabled: false,
              preFilter: [
              ],
              gridConfig: {
                  columnAction: false,
                  hideColumns: ['departure_unicode', 'effective_unicode', 'commission_unicode', 'elective_unicode', 'ativo'],
                  hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'filter'],
              }
          });
      }
      return this._employeeField;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                  this.getContentPanel()
                ]
            });

        return this._formPanel;
    },

    getContentPanel: function() {
        if(!this._contentPanel)
            this._contentPanel = Ext._create('Ext.Panel', {
                title: 'Avaliação',
                items: [
                    {
                        allowBlank: false,
                        name: "content",
                        xtype: "ckeditor",
                        height: 400
                    }
                ]
            });

        return this._contentPanel;
    },

    objectId: function(value, prevent) {
        prevent = core.nullValue(prevent, false);

        if(value !== undefined) {
            this._assessment = value;

            if(!prevent) this.observeArchivement();
        }

        return this._assessment;
    },

    observeArchivement: function() {

    },

    sign: function() {
        var originalCallback = this.callback;

        this.callback = {
            success: {
                scope: this,
                fn: function(instance) {
                    var me = this;
                    this.callback = originalCallback;

                    setTimeout(
                        function() { me._sign(); },
                        50
                    );

                    this.action = 'update';
                    this.buttons.forEach(function(btn) { btn.enable(); });
                }
            }
        };

        this.buttons.forEach(function(btn) { btn.disable(); });
        this.save(true);
    },

    _sign: function() {
        var rest = this.factoryRestful();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Concluindo...'});
        var me = this;

        mask.show();
        rest.sign(
            this.objectId(),
            {
                scope: this,
                fn: function(rst) {
                    Ext.Msg.show({
                        title: 'Concluindo',
                        msg: rst.message,
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function(message) {
                    Ext.Msg.show({
                        title: 'Concluindo',
                        msg: message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                }
            },
            {
                scope: this,
                fn: function() {
                    core.invokeCallback((this.callback || {}).success);
                    mask.hide();
                    me.close();
                }
            }
        );
    },

    getLeftButtons: function(cfg) {
        if(!this._leftButtons)
          this._leftButtons = [
              {
                  text: 'Concluir Avaliação',
                  scope: this,
                  handler: function() {
                      this.sign();
                  }
              }
          ];

        return this._leftButtons;
    },

    getButtons: function(cfg) {
        if(!this._buttons)
          this._buttons = [
              this.getLeftButtons(cfg),
              '->',
          ].concat(corregedoria.cirdir.health.assessment.Window.superclass.getButtons.call(this, cfg));

        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            buttonAlign: 'left',
            border: false,
            disableSaveAndNew: true,
            saveAndContinue: {
              scope: this,
              fn: function(instance) {
                  this.oId = instance.pk;
                  this.action = 'update';
                  this.objectId(instance.pk);
              }
          }
        });

        corregedoria.cirdir.health.assessment.Window.superclass.constructor.call(this, cfg);
        this.objectId(cfg.oId || null);
    }
});
