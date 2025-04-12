Ext._define('rh.gratifications_manager.diligence.Window', {
    extend: 'rh.movimentacao.pessoal.Window',

    rest: 'rh.gratifications_manager.diligence.Restful',

    width: 550,
    height: 470,

    constructor: function(cfg) {
        rh.gratifications_manager.diligence.Window.superclass.constructor.call(this, cfg);
    },

    getPanelInformationItems: function(cfg_window){
        var items = rh.gratifications_manager.diligence.Window.superclass.getPanelInformationItems.call(this, cfg_window);
        items.push(Ext._create('core.fields.AutocompleteField', {
            fieldLabel: "Comarca *",
            allowBlank: false,
            rest: "rh.comarca.ComarcaRestful",
            name: "comarca"
        }));
        items.push(Ext._create('core.fields.AutocompleteField', {
            fieldLabel: "Substituto",
            allowBlank: true,
            rest: "rh.employee.Restful",
            name: "substituto"
        }));
        items.push(Ext._create('core.fields.AutocompleteField', {
            fieldLabel: "Publicação",
            allowBlank: false,
            rest: "rh.publicacao.Restful",
            name: "publicacao",
        }));
        items.push({
            allowBlank: true,
            fieldLabel: "Data Inicio *",
            name: "data_inicio",
            xtype: "datefield"
        });
        items.push({
            allowBlank: true,
            fieldLabel: "Data Fim",
            name: "data_fim",
            xtype: "datefield"
        });
        return items;
    },

    getTabPanel: function(cfg_window, cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                height: 400,
            }
        );
        return rh.gratifications_manager.diligence.Window.superclass.getTabPanel.call(this, {}, cfg);
    },

    getJobPosition: function(cfg_window, cfg) {
        if(!this._jobPositionField){
            cfg = core.nullValue(cfg, {});
            Ext.applyIf(
                cfg, 
            );
            this._jobPositionField = Ext._create('core.fields.AutocompleteField', cfg);
        }
        return this._jobPositionField;
    },
});