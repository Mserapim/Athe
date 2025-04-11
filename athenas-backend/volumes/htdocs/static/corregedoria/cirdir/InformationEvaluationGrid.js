Ext._define('corregedoria.cirdir.InformationEvaluationGrid', {
    extend: 'core.RestfulGrid',

    rest: 'corregedoria.cirdir.InformationEvaluationRestful',
    restWindow: 'corregedoria.cirdir.InformationEvaluationWindow',

    configOrderToolBar: ['accept', '-', 'reject', '-', 'search', '->',],

    getAcceptAction: function(cfg) {
        if(!this._acceptAction) {
            this._acceptAction = new Ext.Button({
                xtype: 'button',
                text: 'Aceitar',
                iconCls: 'icon-crgmpe icon-crgmpe-settings',
                scope: this,
                handler: function() { this.accept(this.getSelectionModel().getSelected(), true);  }
            });       
        }
        return this._acceptAction;
    },

    getRejectAction: function(cfg) {
        if(!this._rejectAction) {
            this._rejectAction = new Ext.Button({
                xtype: 'button',
                text: 'Rejeitar',
                iconCls: 'icon-crgmpe icon-crgmpe-settings',
                scope: this,
                handler: function() { this.accept(this.getSelectionModel().getSelected(), false);  }
            });       
        }
        return this._rejectAction;
    },

    accept: function(selected, bool) {
        
        if(selected) {
            
            Ext.Ajax.request({
                scope: this,
                url: core.callAction('CIRDIRInformationEvaluation', 'to_accept'),
                callback: function() {
                    this.getStore().reload();
                },
                success: function(request) {
                    var rst = Ext.decode(request.responseText);                    
                    Ext.Msg.show({
                        title: 'Conferindo Informação',
                        msg: rst.message,
                        icon: rst.success ? Ext.Msg.INFO : Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                    core.invokeCallback((this.callback || {}).success);
                },
                failure: function(request) {
                    var rst = Ext.decode(request.responseText);
                    Ext.Msg.show({
                        title: 'Conferindo Informação',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                },
                params: {
                    pk: selected.get('pk'),
                    accept: bool
                },
            });
        } else {
            Ext.Msg.show({
                title: 'Conferindo Informação',
                msg: 'Selecione um registro.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {header: '', dataIndex: 'unicode', id: 'autoExpandColumn', },
                ]
            );
        return this._columnModel;
    },

});

core.RestfulGrid.register(
    'corregedoria.cirdir.InformationEvaluationRestful',
    'corregedoria.cirdir.InformationEvaluationGrid'
);
