Ext._define('rh.employee.specialized.tab.BasePanel', {
    extend: 'rh.employee.specialized.tab.RawBasePanel',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                layout: 'border',
                region: 'center',
                border: false,
                scope: this,
            }
        );
        rh.employee.specialized.tab.BasePanel.superclass.constructor.call(this, cfg);
    },

    _newSearch: function(){
        this.getManagerTab().setTabPanel({
            oId: undefined,
            employeePk: undefined,
            employeeRegistry: undefined,
            naturalPersonPk: undefined,
            is_member: undefined,
            action: 'search'
        });
    },

    _new: function(){
        this.getManagerTab().setTabPanel({
            oId: undefined,
            employeePk: undefined,
            employeeRegistry: undefined,
            naturalPersonPk: undefined,
            action: 'create'
        });
    },

    getNewSearchButton: function(){
        return {
            text: "Nova pesquisa",
            handler: this._newSearch,
            scope: this
        };
    },

    getNewButton: function(){
        return {
            text: "Novo",
            handler: this._new,
            scope: this
        };
    },

    getSaveButton: function(){
        return {
            text: "Salvar",
            handler: this._save,
            scope: this
        };
    },

    getButtons: function(){
        return [
            this.getNewSearchButton(),
            this.getNewButton(),
            this.getSaveButton(),
        ];
    },

    getFormPanel: function(){
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                labelAlign:'left',
                items: this.getItemsFormPanel(),
            });
        return this._formPanel;
    },

    getItemsFormPanel: function(){
        if(!this._itemsFormPanel)
            this._itemsFormPanel = [];
        return this._itemsFormPanel;
    },

});
