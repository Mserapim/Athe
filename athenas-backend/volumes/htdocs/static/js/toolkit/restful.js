/**
 *
 */

Ext.ns('toolkit.restful');

toolkit.restful.FormPanel = Ext.extend(
    Ext.Window,
    {
        getFormPanel: function() {
            if(!this.formPanel)
                this.formPanel = new Ext.form.FormPanel({
                });
                
            return this.formPanel;
        },

        getBaseParams: function() {
            return this.baseParams ? this.baseParams : null;    
        },
        
        save: function() {
            
            var form = this.getFormPanel().getForm();
            
            form.waitMsgTarget = this.getEl();
            form.submit({
                scope: this,
                params: this.getBaseParams(),
                url: this.router,
                method: this.method == 'GET' ? this.method : 'POST',
                headers: {
                    'Restful-Method': this.method
                },
                waitMsg: 'Salvando dados na base de dados.',
                success: function(form, action) {
                    var scope = {};
                    
                    if(this.scope)
                        scope = this.scope;
                    
                    scope.__cb__ = this.callback;
                    scope.__cb__(action.result);
                    this.destroy();
                },
                failure: function(form, action) {
                    if(action.result)
                        alert('Ocorreu o seguinte erro tendando gravar os dados:\n\nE: ' + action.result.message);
                    else
                        if(action.failureType == 'client')
                            alert('Erro de valização de dados. Verifique o preenchimento do formulário.')
                        else
                            alert('Parece que o servidor esta passando por dificuldades, tente novamente mais tarde.')
                }
            })
            
        },
        
        constructor: function(cf) {
            
            if(!cf) cf = {};
            
            var df = {
                pk: null,
                values: {},
                method: 'POST',
                callback: function() {},
                title: 'undefined',
                closable: true,
                resizable: true,
                shadow: false,
                buttons: [
                    {
                        text: 'Salvar',
                        scope: this,
                        handler: this.save
                    },
                    {
                        text: 'Cancelar',
                        scope: this,
                        handler: this.destroy
                    }
                ]
            };
            
            Ext.applyIf(cf, df);
            
            toolkit.restful.FormPanel.superclass.constructor.call(this, cf);
            
            this.add(this.getFormPanel());
            
        }
    }
);