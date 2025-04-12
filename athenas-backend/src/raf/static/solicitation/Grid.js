Ext._define('raf.solicitation.Grid', {
    extend: 'core.RestfulGrid',

    restWindow: 'raf.solicitation.Window',

    configOrderToolBar: ['-', 'search', 'reopen'],

    getReopenAction: function(cfg) {
        if(!this._reopenAction)
            this._reopenAction = Ext._create('Ext.Button', {
                text: 'Reabrir',
                iconCls: 'icon-raf icon-raf-copy',
                scope: this,
                handler: function() {
                    this.reopenRaf();
                }
            });

        return this._reopenAction;
    },

    reopenRaf: function() {
        var selected = this.getSelectionModel().getSelected();
                
        if(selected) {
            
            Ext.Msg.show({
                title: 'Reabrir RAF',
                msg: 'Tem certeza que aceita a reabertura do RAF selecionado?',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                scope: this,
                fn: function(btn) {
                    if(btn=='no') return;
                    
                    this.reopenRequest(selected);
                }
            });
        } else {
            Ext.Msg.show({
                title: 'Reabrir RAF',
                msg: 'Primeiro selecione a solicitação',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
        }
    },

    reopenRequest: function(selected) {
        Ext.Ajax.request({
            scope: this,
            url: core.callAction('RAFSolicitation', 'accept_reopen'),
            callback: function() {
                core.invokeCallback((this.callback || {}).success);
                this.getStore().reload();
            },
            success: function(request) {
                var rst = Ext.decode(request.responseText);

                Ext.Msg.show({
                    title: 'Reabrir RAF',
                    msg: rst.message,
                    icon: rst.success ? Ext.Msg.INFO : Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            },
            failure: function(request) {
                var rst = Ext.decode(request.responseText);
                Ext.Msg.show({
                    title: 'Reabrir RAF',
                    msg: rst.message,
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK
                });
            },
            params: {
                solicitation: selected.get('pk')
            },
        });
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = new Ext.grid.ColumnModel({
                columns: [
                    {
                      header: 'Solicitação',
                      dataIndex: 'unicode',
                      id: 'autoExpandColumn',
                      sortable: false,
                      menuDisabled: true,
                    },
                ],
            });
        return this._columnModel;
    },


});

core.RestfulGrid.register(
    'raf.solicitation.Restful',
    'raf.solicitation.Grid'
);
