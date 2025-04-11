Ext._define('judicial.remittance.RemittanceItselfOrganWindow', {
    extend: 'judicial.PartLawsuitActionWindow',
    rest: 'judicial.remittance.RemittanceItselfOrganRestful',
    mixins: {'1': 'judicial.remittance.RemitToMixin'},

    width: 900,
    autoCreate: true,

    getMainPanel: function(cfg) {
        if(!this._mainPanel)
            this._mainPanel = Ext._create('Ext.Panel', {
                title: 'Principal',
                border: false,
                items: [
                    {
                        xtype: 'panel',
                        frame: true,
                        layout: 'form',
                        items: [
                            this.getRemitToField()
                        ]
                    },
                ]
            });

        return this._mainPanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getRemitToField()
                ]
            });

        return this._formPanel;
    },

    readDataCallback: function(inst) {
        this.readDataCallback(inst.pk);
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
        });

        judicial.remittance.RemittanceItselfOrganWindow.superclass.constructor.call(this, cfg);
    }
});

judicial.PartLawsuitGrid.register('judicial.remittanceitselforgan', 'judicial.remittance.RemittanceItselfOrganWindow');
