Ext._define('judicial.remittance.ArchivingRemittanceWindow', {
    extend: 'judicial.PartLawsuitActionWindow',
    rest: 'judicial.remittance.ArchivingRemittanceRestful',
    mixins: {'1': 'judicial.remittance.RemitToMixin'},

    width: 900,

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

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            title: 'Remessa com arquivamento',
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
        });

        judicial.remittance.ArchivingRemittanceWindow.superclass.constructor.call(this, cfg);
    }
});

judicial.PartLawsuitGrid.register('judicial.archivingremittance', 'judicial.remittance.ArchivingRemittanceWindow');
