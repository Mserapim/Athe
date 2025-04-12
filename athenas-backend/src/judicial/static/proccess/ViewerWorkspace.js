
Ext._define('judicial.proccess.ViewerWorkspace', {
    statics: {
        workspace: null,

        _createWorkspace: function(executionOrgan, mode) {
            var pPortrait = (window.innerWidth / window.innerHeight);
            var pLandscape =  (window.innerHeight / window.innerWidth);
            var self = judicial.proccess.ViewerWorkspace;

            self.WorkspaceClass =  null;

            if (pLandscape > pPortrait) {
                self.WorkspaceClass = 'judicial.proccess.PortraitWorkspace';
            } else {
                self.WorkspaceClass = 'judicial.proccess.LandscapeWorkspace';
            }

            self.workspace = Ext._create(self.WorkspaceClass, {
                executionOrgan: executionOrgan,
                adminMode: mode === 'admin',
                mode: mode,
                windowConfig: function() { return window.config(); }
            });

            var bodyEl = document.querySelector('body');

            bodyEl.onresize = function(e) {
                self.workspace.destroy();
                judicial.proccess.ViewerWorkspace._createWorkspace(
                    executionOrgan,
                    mode
                );
            };
        },

        readProcessInformation: function(data, rest) {

            rest.doRequest(
                rest.getRoute(
                    'read',
                    data.id,
                    'GET',
                    {
                        params: {
                            execution_organ: data.execution_organ,
                            data_mode: data.mode
                        },
                        success: function(xhr) {
                            var rst = Ext.decode(xhr.responseText);
                            var self = judicial.proccess.ViewerWorkspace;

                            if(rst.success){
                                window.config = function() {
                                    return rst.instance;
                                };

                                self._createWorkspace(
                                    (data.execution_organ || null),
                                    data.mode
                                );

                                document.getElementById('container_loading').style.display = 'none';
                            } else {
                                document.getElementById('container_loading').style.display = 'none';
                                document.getElementById('container_error').style.display = 'block';
                            }
                        },
                        failure: function() {
                            Ext.Msg.show({
                                title: 'Recuperando procedimento',
                                msg: 'Recurso indisponível no momento.',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                fn: function(btn) {
                                    if (btn === 'ok') window.close();
                                }
                            });
                        }
                    }
                )
            );
        },

        receiveMovement: function(data, rest) {
            rest.doRequest(
                rest.getRoute(
                    'receive_movement',
                    false,
                    'PUT',
                    {
                        params: {
                            pk: data.id,
                            rest_resource: rest.resource
                        },
                        scope: this,
                        success: function(xhr) {
                            var rst = Ext.decode(xhr.responseText);

                            if(rst.success)
                                judicial.proccess.ViewerWorkspace.readProcessInformation(data, rest);
                            else
                                Ext.Msg.show({
                                    title: 'Erro',
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK,
                                    msg: rst.message
                                });
                        },
                        failure: function() {
                            Ext.Msg.show({
                                title: 'Erro',
                                icon: Ext.Msg.ERROR,
                                buttons: Ext.Msg.OK,
                                msg: 'Recurso indisponivel no momento.'
                            });
                        },
                        callback: function() {}
                    }
                )
            );
        },

        init: function() {
            var data = location.hash.substr(1);

            if(data.indexOf('/') >= 0)
                data = {
                    id: location.hash.substr(1).split('/')[2],
                    execution_organ: location.hash.substr(1).split('/')[1],
                    mode: location.hash.substr(1).split('/')[0]
                };
            else
                data = {
                    id: location.hash.substr(1),
                    mode: 'read'
                };

            var rest;
            if(data.mode == 'admin')
                rest = Ext._create('judicial.outcourtlawsuit.OutCourtLawsuitAdminRestful');
            else if(data.mode == 'officer')
                rest = Ext._create('judicial.outcourtlawsuit.OutCourtLawsuitOfficerRestful');
            else
                rest = Ext._create('judicial.OutCourtLawsuitRestful');

            judicial.proccess.ViewerWorkspace.receiveMovement(data, rest);

            Ext.QuickTips.init();
        }
    }
});
