
Ext._define('judicial.outcourtlawsuit.LawsuitMatterGrid', {
    extend: 'core.RestfulGrid',

    restWindow: 'judicial.outcourtlawsuit.LawsuitMatterWindow',

    configOrderToolBar: ['search', 'definePrincipal'],
    

    getDefinePrincipalAction: function(cfg) {
        if(!this._definePrincipal)
            this._definePrincipal = Ext._create('Ext.Button', {
                text: 'Definir principal',
                iconCls: 'icon-judicial icon-ejud-active',
                scope: this,
                handler: this.definePrincipal
            });

        return this._definePrincipal;
    },

    definePrincipal: function() {
        
        var rest = this.factoryRestful();
        var mask =  null;
        var selected = this.getSelectionModel().getSelected();
                
        var configAlert = (function(message) {
            return {
                title: 'Definir assunto principal',
                msg: message,
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            };
        });


        if(selected) {
            mask =  new Ext.LoadMask(this.getEl(), {msg: 'definindo assunto principal...'});
            mask.show();
            
            rest.definePrincipal(
                selected.get('pk'),
                this.getParams(),
                {
                    scope: this,
                    fn: function(rst) {
                        if(rst.success) {
                            core.invokeCallback((this.callback || {}).success);
                            this.getStore().reload();
                        }
                        else
                            Ext.Msg.show(configAlert(rst.message));
                    }
                },
                {
                    scope: this,
                    fn: function(message) {
                        Ext.Msg.show(configAlert(message));
                    }
                },
                {
                    scope: this,
                    fn: function() {
                        mask.hide();
                    }
                }
            );
        } else {
            Ext.Msg.show(configAlert('Primeiro selecione um assunto.'));
        }
    },

    getColumnModel: function() {
        if(!this._columnModel)
            this._columnModel = Ext._create(
                'Ext.grid.ColumnModel',
                [
                    Ext._create('Ext.grid.RowNumberer'),
                    {
                        header: '',
                        dataIndex: 'icons',
                        width: 24,
                        menuDisabled: true,
                        renderer: core.rendererIconGrid,
                        hidden: false
                    },
                    {header: 'Assunto', dataIndex: 'unicode', id: 'autoExpandColumn'}
                ]
            );

        return this._columnModel;
    }
});

core.RestfulGrid.register(
    'judicial.outcourtlawsuit.LawsuitMatterRestful',
    'judicial.outcourtlawsuit.LawsuitMatterGrid'
);

