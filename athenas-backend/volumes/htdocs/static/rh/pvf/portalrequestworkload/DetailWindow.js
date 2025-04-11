Ext._define('rh.pvf.portalrequestworkload.DetailWindow', {
    extend:'rh.pvf.portalrequest.DetailWindow',

    rest: 'rh.pvf.portalrequestworkload.Restful',

    height: 620,

    getFieldSet:function(cfg){
        return this.getWorkLoadFieldSet(cfg)
    },


    getWorkLoadFieldSet: function (cfg) {
        if (!this._marked)
            this._marked = Ext._create('Ext.form.FieldSet', {
                title: 'Carga Horária',
                items: [
                    {
                        fieldLabel: 'Jornada Atual',
                        xtype: 'displayfield',
                        value:cfg.data.old_workload+"h"
                        
                    },
                    {
                        fieldLabel: 'Nova Jornada',
                        xtype: 'displayfield',
                        value:cfg.data.to_workload+"h"
                        
                    },
                    {
                        fieldLabel: 'Data de Início',
                        xtype: 'displayfield',
                        value: Ext.util.Format.date(cfg.data.date_work_load, 'd/m/Y')
                    },
                   
                ]
            });

        return this._marked;
    },

});