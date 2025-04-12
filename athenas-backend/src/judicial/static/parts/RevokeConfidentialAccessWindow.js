
Ext._define('judicial.parts.RevokeConfidentialAccessWindow', {
    extend: 'judicial.parts.ConfidentialAccessWindow',

    rest: 'judicial.parts.RevokeConfidentialAccessRestful',

    width: 900,

    autoCreate: true,

    observer: function() {
        var instance = this.confidential();
        var selection = this.selection();
        var clear = false;

        if(selection == 2) {
            this.getControlPanel().enable();
            this.getPartLawsuitGrid().enable();
            this.getPartLawsuitSelectedGrid().enable();
            clear = false;
        } else {
            this.getControlPanel().disable();
            this.getPartLawsuitGrid().disable();
            this.getPartLawsuitSelectedGrid().disable();
            clear = true;
        }

        if(instance) {

            this.getPartLawsuitGrid().setFilterProperty('access_controls__isnull', false, 1000, false);
            this.getPartLawsuitGrid().setFilterProperty('access_controls__in_revokeconfidentialaccess', instance, -1001, false);
            this.getPartLawsuitGrid().setFilterProperty('access_controls__suspended_at__isnull', true, 1002, !clear);
            
            this.getPartLawsuitSelectedGrid().setFilterProperty('access_controls__in_revokeconfidentialaccess', instance, 1000, !clear);
            
            if(clear){
                this.getPartLawsuitGrid().getStore().removeAll({});
                this.getPartLawsuitSelectedGrid().getStore().removeAll({});
            }

        } else {
            this.getPartLawsuitGrid().getStore().removeAll({});
            this.getPartLawsuitSelectedGrid().getStore().removeAll({});
        }

    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.apply(cfg, {
            title: 'Desclassificação de Sigilo'
        });

        judicial.parts.RevokeConfidentialAccessWindow.superclass.constructor.call(this, cfg);
    }

});

judicial.PartLawsuitGrid.register('judicial.revokeconfidentialaccess', 'judicial.parts.RevokeConfidentialAccessWindow');
