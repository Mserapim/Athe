/**
 *
 **/
Ext._define('adm.patrimonio.localizacao.FilterWindow', {
    extend: 'Ext.Window',

    getLocalizacaoPanel: function() {
        if(!this._localizacaoPanel) {
            this._localizacaoPanel = Ext._create('adm.patrimonio.localizacao.Tree', {
                flex: 1.0,
                bodyStyle: {
                    'border-right': 0
                }
            });

            this._localizacaoPanel.getToolbar().removeAll();
        }

        return this._localizacaoPanel;
    },

    doSelectSingle: function() {
        var selection = this.getLocalizacaoPanel().getSelectionModel().getSelectedNode();
        var tupla = [selection.id];

        core.invokeCallback(this.callback, tupla);
        this.destroy();
    },

    doSelectWithChild: function() {
        var rest = Ext._create('adm.patrimonio.localizacao.Restful', {});
        var selection = this.getLocalizacaoPanel().getSelectionModel().getSelectedNode();
        var cfg = rest.getRoute('childs', selection.id);

        Ext.apply(cfg, {
            scope: this,
            success: function(request) {
                var rst = Ext.decode(request.responseText);
                var tupla = [selection.id];
                if(rst.success) {
                    tupla = tupla.concat(rst.collection.map(function(data) { return data.pk; }));
                    core.invokeCallback(this.callback, tupla);
                    this.destroy();
                }
                else
                    Ext.Msg.show({
                        title: 'Buscando',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: rst.message
                    });
            },
            failure: function() {
                Ext.Msg.show({
                    title: 'Buscando...',
                    icon: Ext.Msg.ERROR,
                    buttons: Ext.Msg.OK,
                    msg: 'Recurso indisponível no momento. Tente mais tarde novamente.'
                });
            }
        });

        rest.doRequest(cfg);
    },

    doSelect: function() {
        var selection = this.getLocalizacaoPanel().getSelectionModel().getSelectedNode();

        if(selection && !selection.leaf)
            Ext.Msg.show({
                title: 'Filtrando por Localização',
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                msg: 'Deseja incluir as filhas da localização selecionada',
                scope: this,
                fn: function(b) {
                    if(b == 'yes')
                        this.doSelectWithChild();
                    else
                        this.doSelectSingle();
                }
            });
        else if(selection && selection.leaf)
            this.doSelectSingle();
        else {
            core.invokeCallback(this.callback, false);
            this.destroy();
        }
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Selecionar Localizações'
            }
        );

        Ext.apply(
            cfg,
            {
                width: 650,
                layout: 'hbox',
                border: false,
                defaults: {
                    height: 450,
                },
                items: [
                    this.getLocalizacaoPanel()
                ],
                buttons: [
                    {
                        text: 'Selecionar',
                        scope: this,
                        handler: this.doSelect
                    },
                    {
                        text: 'Fechar',
                        scope: this,
                        handler: this.destroy
                    }
                ]
            }
        );

        // this.callParent([cfg]);
        adm.patrimonio.localizacao.FilterWindow.superclass.constructor.call(this, cfg);
    }
});
